from typing import TYPE_CHECKING
import elastix_napari.utils as utils
from enum import Enum
import numpy as np
from napari_plugin_engine import napari_hook_implementation
from magicgui import magic_factory
import itk
from pathlib import Path
from typing import Sequence
from itk_napari_conversion import image_from_image_layer
from itk_napari_conversion import image_layer_from_image


def on_init(widget):
    """
    Initializes widget layout.
    Updates widget layout according to user input.
    """
    widget.native.setStyleSheet("QWidget{font-size: 12pt;}")

    for x in ['fixed_mask', 'moving_mask', 'param1', 'param2', 'param3',
              'fixed_ps', 'moving_ps', 'metric', 'init_trans',
              'resolutions', 'max_iterations', 'nr_spatial_samples',
              'max_step_length']:
        setattr(getattr(widget, x), 'visible', False)

    def toggle_mask_widgets(event):
        for x in ['fixed_mask', 'moving_mask']:
            setattr(getattr(widget, x), 'visible', event.value)

    def toggle_preset_widget(event):
        if event.value == "custom":
            for x in ['param1', 'param2', 'param3']:
                setattr(getattr(widget, x), 'visible', True)
            for y in ['metric', 'resolutions', 'max_iterations',
                      'nr_spatial_samples', 'max_step_length']:
                setattr(getattr(widget, y), 'visible', False)

        else:
            for x in ['param1', 'param2', 'param3']:
                setattr(getattr(widget, x), 'visible', False)
            for x in ['metric', 'init_trans', 'resolutions', 'max_iterations',
                      'nr_spatial_samples', 'max_step_length', 'moving_ps',
                      'fixed_ps']:
                setattr(getattr(widget, x), 'visible', widget.advanced.value)

    def toggle_advanced_widget(event):
        if widget.preset.value == "custom":
            for x in ['init_trans', 'fixed_ps', 'moving_ps']:
                setattr(getattr(widget, x), 'visible', event.value)
        else:
            for x in ['metric', 'init_trans', 'resolutions',
                      'max_iterations', 'nr_spatial_samples',
                      'max_step_length', 'fixed_ps', 'moving_ps']:
                setattr(getattr(widget, x), 'visible', event.value)

    widget.preset.changed.connect(toggle_preset_widget)
    widget.masks.changed.connect(toggle_mask_widgets)
    widget.advanced.changed.connect(toggle_advanced_widget)
    widget.native.layout().addStretch()


@magic_factory(widget_init=on_init, layout='vertical', call_button="register",
               preset={"choices": ["rigid", "affine", "bspline", "custom"],
                       "tooltip": "Select a preset parameter file or select "
                       "the 'custom' option to load a custom one"},
               fixed_ps={"label": "fixed point set", "filter": "*.txt",
                         "tooltip": "Load a fixed point set"},
               moving_ps={"label": "moving point set", "filter": "*.txt",
                          "tooltip": "Load a moving point set"},
               param1={"label": "parameterfile 1", "filter": "*.txt",
                       "tooltip": 'Load a custom parameter file'},
               param2={"label": "parameterfile 2", "filter": "*.txt",
                       "tooltip": 'Optionally load a second custom parameter '
                       'file'},
               param3={"label": "parameterfile 3", "filter": "*.txt",
                       "tooltip": 'Optionally load a third custom parameter '
                       'file'},
               metric={"choices": ["AdvancedMattesMutualInformation",
                                   "AdvancedNormalizedCorrelation",
                                   "AdvancedMeanSquares"],
                       "tooltip": 'Select a metric to use'},
               init_trans={"label": "initial transform", "filter": "*.txt",
                           "tooltip": 'Load a initial transform from a .txt '
                           'file'},
               nr_spatial_samples={"max": 8192, "step": 256,
                                   "tooltip": 'Select the number of spatial '
                                   'samples to use'})
def elastix_registration(fixed: 'napari.layers.Image',
                         moving: 'napari.layers.Image', preset: str,
                         fixed_mask: 'napari.layers.Image',
                         moving_mask: 'napari.layers.Image',
                         fixed_ps: Sequence[Path], moving_ps: Sequence[Path],
                         param1: Sequence[Path], param2: Sequence[Path],
                         param3: Sequence[Path], init_trans: Sequence[Path],
                         metric: str = "AdvancedMattesMutualInformation",
                         resolutions: int = 4, max_iterations: int = 500,
                         nr_spatial_samples: int = 512,
                         max_step_length: float = 1.0,  masks: bool = False,
                         advanced: bool = False
                         ) -> 'napari.layers.Image':
    """
    Takes user input and calls elastix' registration function in itkelastix.
    """
    if fixed is None or moving is None:
        print("No images selected for registration.")
        return utils.error("No images selected for registration.")
    if utils.check_filename(fixed_ps) != utils.check_filename(moving_ps):
        print("Select both fixed and moving point set.")
        return utils.error("Select both fixed and moving point set.")

    if advanced:
        if utils.check_filename(init_trans):
            init_trans = str(init_trans[0])
        else:
            init_trans = ''
        if utils.check_filename(fixed_ps):
            fixed_ps = str(fixed_ps[0])
        else:
            fixed_ps = ''
        if utils.check_filename(moving_ps):
            moving_ps = str(moving_ps[0])
        else:
            moving_ps = ''
    else:
        init_trans = ''
        fixed_ps = ''
        moving_ps = ''

    # Convert image layer to itk_image
    fixed = image_from_image_layer(fixed)
    moving = image_from_image_layer(moving)
    fixed = fixed.astype(itk.F)
    moving = moving.astype(itk.F)

    parameter_object = itk.ParameterObject.New()
    if preset == "custom":
        for par_sequence in [param1, param2, param3]:
            par = str(par_sequence[0])
            if ".txt" in par:
                try:
                    parameter_object.AddParameterFile(par)
                except:
                    return utils.error("Parameter file not found or not valid")
            else:
                pass
    else:
        if advanced:
            parameter_map = \
                parameter_object.GetDefaultParameterMap(preset, resolutions)
            parameter_map['Metric'] = [metric]
            if fixed_ps != '' and moving_ps != '':
                parameter_map['Registration'] = [
                    'MultiMetricMultiResolutionRegistration']
                original_metric = parameter_map['Metric']
                parameter_map['Metric'] = \
                    [original_metric[0],
                        'CorrespondingPointsEuclideanDistanceMetric']
            parameter_map['MaximumStepLength'] = [str(max_step_length)]
            parameter_map['NumberOfSpatialSamples'] = [str(nr_spatial_samples)]
            parameter_map['MaximumNumberOfIterations'] = [str(max_iterations)]
        else:
            parameter_map = parameter_object.GetDefaultParameterMap(preset)
        parameter_object.AddParameterMap(parameter_map)

    if not masks:
        result_image, result_transform_parameters = \
            itk.elastix_registration_method(
                fixed, moving, parameter_object,
                fixed_point_set_file_name=fixed_ps,
                moving_point_set_file_name=moving_ps,
                initial_transform_parameter_file_name=init_trans,
                log_to_console=True)

    elif masks:
        if fixed_mask is None and moving_mask is None:
            print("No masks selected for registration")
            return utils.error("No masks selected for registration")
        else:
            if moving_mask is None:
                # Convert mask layer to itk_image
                fixed_mask = image_from_image_layer(fixed_mask)
                fixed_mask = fixed_mask.astype(itk.UC)

                # Call elastix
                result_image, rtp = itk.elastix_registration_method(
                    fixed, moving, parameter_object, fixed_mask=fixed_mask,
                    fixed_point_set_file_name=fixed_ps,
                    moving_point_set_file_name=moving_ps,
                    initial_transform_parameter_file_name=init_trans,
                    log_to_console=False)

            elif fixed_mask is None:
                # Convert mask layer to itk_image
                moving_mask = image_from_image_layer(moving_mask)
                moving_mask = moving_mask.astype(itk.UC)

                # Call elastix
                result_image, rtp = itk.elastix_registration_method(
                    fixed, moving, parameter_object, moving_mask=moving_mask,
                    fixed_point_set_file_name=fixed_ps,
                    moving_point_set_file_name=moving_ps,
                    initial_transform_parameter_file_name=init_trans,
                    log_to_console=False)
            else:
                # Convert mask layer to itk_image
                fixed_mask = image_from_image_layer(fixed_mask)
                fixed_mask = fixed_mask.astype(itk.UC)
                moving_mask = image_from_image_layer(moving_mask)
                moving_mask = moving_mask.astype(itk.UC)

                # Call elastix
                result_image, rtp = itk.elastix_registration_method(
                    fixed, moving, parameter_object, fixed_mask=fixed_mask,
                    moving_mask=moving_mask,
                    fixed_point_set_file_name=fixed_ps,
                    moving_point_set_file_name=moving_ps,
                    initial_transform_parameter_file_name=init_trans,
                    log_to_console=False)

    layer = image_layer_from_image(result_image)
    layer.name = preset + " Registration"
    return layer


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return elastix_registration
