"""
This module is an example of a barebones function plugin for napari

It implements the ``napari_experimental_provide_function`` hook specification.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below according to your needs.
"""
from typing import TYPE_CHECKING

from enum import Enum
import numpy as np
from napari_plugin_engine import napari_hook_implementation
from magicgui import magic_factory
import itk
from pathlib import Path
from typing import Sequence


def on_init(widget):
    widget.native.setStyleSheet("QWidget{font-size: 12pt;}")

    for x in ['fixed_mask', 'moving_mask', 'param1', 'param2', 'param3',
              'fixed_ps', 'moving_ps', 'metric', 'optimizer', 'init_trans',
              'resolutions', 'max_iterations']:
        setattr(getattr(widget, x), 'visible', False)

    def toggle_mask_widgets(event):
        if event.value == "none":
            widget.fixed_mask.visible = False
            widget.moving_mask.visible = False
            widget.fixed_ps.visible = False
            widget.moving_ps.visible = False
        elif event.value == "masks":
            widget.fixed_mask.visible = True
            widget.moving_mask.visible = True
            widget.fixed_ps.visible = False
            widget.moving_ps.visible = False
        elif event.value == "pointset":
            widget.fixed_mask.visible = False
            widget.moving_mask.visible = False
            widget.fixed_ps.visible = True
            widget.moving_ps.visible = True

    def toggle_preset_widget(event):
        if event.value == "custom":
            widget.param1.visible = True
            widget.param2.visible = True
            widget.param3.visible = True
        else:
            widget.param1.visible = False
            widget.param2.visible = False
            widget.param3.visible = False

    def toggle_advanced_widget(event):
        for x in ['metric', 'optimizer', 'init_trans', 'resolutions',
                  'max_iterations']:
            setattr(getattr(widget, x), 'visible', event.value)

    widget.preset.changed.connect(toggle_preset_widget)
    widget.focus.changed.connect(toggle_mask_widgets)
    widget.advanced.changed.connect(toggle_advanced_widget)
    widget.native.layout().addStretch()


@magic_factory(widget_init=on_init, layout='vertical', call_button="register",
               preset={"choices": ["rigid", "affine", "bspline", "custom"]},
               focus={"choices": ["none", "pointset", "masks"]},
               fixed_ps={"label": "fixed point set", "filter": "*.txt"},
               moving_ps={"label": "moving point set", "filter": "*.txt"},
               param1={"label": "parameterfile", "filter": "*.txt"},
               param2={"label": "parameterfile 2", "filter": "*.txt"},
               param3={"label": "parameterfile 3", "filter": "*.txt"},
               metric={"choices": ["default",
                                   "AdvancedMattesMutualInformation",
                                   "AdvancedNormalizedCorrelation",
                                   "AdvancedMeanSquares",
                                   "DisplacementMagnitudePenalty",
                                   "GradientDifference",
                                   "KNNGraphAlphaMutualInformation",
                                   "PatternIntensity",
                                   "PCAMetric2",
                                   "VarianceOverLastDimensionMetric"]},
               optimizer={"choices": ["default",
                                      "AdaptiveStochasticGradientDescent",
                                      "AdaptiveStochasticLBFGS",
                                      "ConjugateGradient", "QuasiNewtonLBFGS",
                                      "RegularStepGradientDescent"
                                      "StandardGradientDescent"]},
               init_trans={"label": "initial transform", "filter": "*.txt"})
def elastix_registration(fixed: 'napari.types.ImageData',
                         moving: 'napari.types.ImageData',
                         fixed_mask: 'napari.types.ImageData',
                         moving_mask: 'napari.types.ImageData',
                         fixed_ps: Sequence[Path], moving_ps: Sequence[Path],
                         param1: Sequence[Path], param2: Sequence[Path],
                         param3: Sequence[Path], preset: str, focus: str,
                         init_trans: Sequence[Path], metric: str,
                         optimizer: str, resolutions: int = 4,
                         max_iterations: int = 500,
                         advanced: bool = False
                         ) -> 'napari.types.LayerDataTuple':

    if fixed is None or moving is None:
        print("No images selected for registration.")
        return

    if advanced and not ('.txt' not in init_trans):
        init_trans = str(init_trans[0])
    else:
        init_trans = ''

    # Casting to numpy is currently necessary
    # because of napari's type ambiguity.
    fixed = np.asarray(fixed).astype(np.float32)
    moving = np.asarray(moving).astype(np.float32)

    parameter_object = itk.ParameterObject.New()
    if preset == "custom":
        for par_sequence in [param1, param2, param3]:
            par = str(par_sequence[0])
            if ".txt" in par:
                try:
                    parameter_object.AddParameterFile(par)
                except:
                    raise TypeError("Parameter file not found or not valid")
            else:
                pass
    else:
        if advanced:
            parameter_map = \
                parameter_object.GetDefaultParameterMap(preset, resolutions)
            if metric != 'default':
                parameter_map['Metric'] = [metric]
            if optimizer != 'default':
                parameter_map['Optimizer'] = [optimizer]
            parameter_map['MaximumNumberOfIterations'] = [str(max_iterations)]
        else:
            parameter_map = parameter_object.GetDefaultParameterMap(preset)
        parameter_object.AddParameterMap(parameter_map)

    if focus == "none":
        result_image, result_transform_parameters = \
            itk.elastix_registration_method(
                fixed, moving, parameter_object,
                initial_transform_parameter_file_name=init_trans,
                log_to_console=True)

    elif focus == "masks":
        if fixed_mask is None and moving_mask is None:
            print("No masks selected for registration")
            return
        else:
            # Casting to numpy and itk is currently necessary
            # because of napari's type ambiguity.

            if moving_mask is None:
                fixed_mask = np.asarray(fixed_mask).astype(np.uint8)
                fixed_mask = itk.image_view_from_array(fixed_mask)
                result_image, rtp = itk.elastix_registration_method(
                    fixed, moving, parameter_object, fixed_mask=fixed_mask,
                    initial_transform_parameter_file_name=init_trans,
                    log_to_console=False)

            elif fixed_mask is None:
                moving_mask = np.asarray(moving_mask).astype(np.uint8)
                moving_mask = itk.image_view_from_array(moving_mask)
                result_image, rtp = itk.elastix_registration_method(
                    fixed, moving, parameter_object, moving_mask=moving_mask,
                    initial_transform_parameter_file_name=init_trans,
                    log_to_console=False)
            else:
                fixed_mask = np.asarray(fixed_mask).astype(np.uint8)
                fixed_mask = itk.image_view_from_array(fixed_mask)
                moving_mask = np.asarray(moving_mask).astype(np.uint8)
                moving_mask = itk.image_view_from_array(moving_mask)

                result_image, rtp = itk.elastix_registration_method(
                    fixed, moving, parameter_object, fixed_mask=fixed_mask,
                    initial_transform_parameter_file_name=init_trans,
                    moving_mask=moving_mask, log_to_console=False)

    elif focus == "pointset":
        if fixed_ps is None and moving_ps is None:
            print("No pointsets selected for registration")
            return
        else:
            if fixed_ps is None:
                moving_ps = str(moving_ps[0])
                result_image, rtp = itk.elastix_registration_method(
                    fixed, moving, moving_point_set_file_name=moving_ps,
                    initial_transform_parameter_file_name=init_trans,
                    log_to_console=False, parameter_object=parameter_object)
            elif moving_ps is None:
                fixed_ps = str(fixed_ps[0])
                result_image, rtp = itk.elastix_registration_method(
                    fixed, moving, fixed_point_set_file_name=fixed_ps,
                    initial_transform_parameter_file_name=init_trans,
                    log_to_console=False, parameter_object=parameter_object)
            else:
                fixed_ps = str(fixed_ps[0])
                moving_ps = str(moving_ps[0])
                result_image, rtp = itk.elastix_registration_method(
                    fixed, moving, fixed_point_set_file_name=fixed_ps,
                    initial_transform_parameter_file_name=init_trans,
                    moving_point_set_file_name=moving_ps, log_to_console=False,
                    parameter_object=parameter_object)

    return np.asarray(result_image).astype(np.float32), {'name': preset + ' ' + focus + ' Registration'}


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return elastix_registration
