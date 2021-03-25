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

    widget.fixed_mask.visible = False
    widget.moving_mask.visible = False
    widget.filenames.visible = False

    def toggle_mask_widgets(event):
        widget.fixed_mask.visible = event.value
        widget.moving_mask.visible = event.value

    def toggle_preset_widget(event):
        if event.value == "custom":
            widget.filenames.visible = True
        else:
            widget.filenames.visible = False

    widget.preset.changed.connect(toggle_preset_widget)
    widget.use_masks.changed.connect(toggle_mask_widgets)
    widget.native.layout().addStretch()


@magic_factory(widget_init=on_init, layout='vertical', call_button="register",
               preset={"choices": ["rigid", "affine", "bspline", "custom"]},
               filenames={"label": "parameterfile (optional):",
               "filter": "*.txt"})
def elastix_registration(fixed: 'napari.types.ImageData',
                         moving: 'napari.types.ImageData',
                         fixed_mask: 'napari.types.ImageData',
                         moving_mask: 'napari.types.ImageData', preset: str,
                         filenames: Sequence[Path], use_masks: bool = False
                         )-> 'napari.types.LayerDataTuple':
    if fixed is None or moving is None:
        print("No images selected for registration.")
        return

    # Casting to numpy is currently necessary
    # because of napari's type ambiguity.
    fixed = np.asarray(fixed).astype(np.float32)
    moving = np.asarray(moving).astype(np.float32)

    parameter_object = itk.ParameterObject.New()
    filename = str(filenames[0])
    if preset == "custom":
        try:
            parameter_object.AddParameterFile(filename)
        except:
            raise TypeError("Parameter file not found or not valid")
    else:
        default_parameter_map = parameter_object.GetDefaultParameterMap(preset)
        parameter_object.AddParameterMap(default_parameter_map)

    if use_masks:
        if fixed_mask is None and moving_mask is None:
            print("No masks selected for registration")
            return
        else:
            # Casting to numpy and itk is currently necessary
            # because of napari's type ambiguity.
            fixed_mask = np.asarray(fixed_mask).astype(np.uint8)
            fixed_mask = itk.image_view_from_array(fixed_mask)
            moving_mask = np.asarray(moving_mask).astype(np.uint8)
            moving_mask = itk.image_view_from_array(moving_mask)

            result_image, result_transform_parameters = \
                itk.elastix_registration_method(
                    fixed, moving, parameter_object, fixed_mask=fixed_mask,
                    moving_mask=moving_mask, log_to_console=False)
    else:
        result_image, result_transform_parameters = \
            itk.elastix_registration_method(fixed, moving, parameter_object,
                                            log_to_console=False)
    return np.asarray(result_image).astype(np.float32), {'name':preset + ' Registration'}


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return elastix_registration, {'area': 'bottom'}
