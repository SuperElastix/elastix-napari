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

# if TYPE_CHECKING:
# from napari.types import ImageData, LabelsData, LayerDataTuple
def on_init(widget):
    widget.native.setStyleSheet("QWidget{font-size: 12pt;}")

@magic_factory(widget_init=on_init, layout='vertical', call_button="register",
                transform = {"choices": ["rigid", "affine", "bspline"]},
                filenames={"label":"parameterfile (optional):", "filter":"*.txt"})
def register(fixed: 'napari.types.ImageData', moving: 'napari.types.ImageData', transform: str, filenames: Sequence[Path]) -> 'napari.types.LayerDataTuple':
    if fixed is None or moving is None:
        print("No images selected for registration.")
        return
    fixed = np.asarray(fixed).astype(np.float32)
    moving = np.asarray(moving).astype(np.float32)
    parameter_object = itk.ParameterObject.New()
    print(type(filenames[0]))
    print(filenames[0])
    filename = str(filenames[0])
    if ".txt" in filename:
        transform = 'custom'
        try:
            parameter_object.AddParameterFile(filename)
        except:
            print("Parameter file not found or not valid.")
    else:
        default_rigid_parameter_map = parameter_object.GetDefaultParameterMap(transform, 3)
        parameter_object.AddParameterMap(default_rigid_parameter_map)
    result_image, result_transform_parameters = itk.elastix_registration_method(
        fixed, moving,
        parameter_object=parameter_object,
        log_to_console=True)
    return np.asarray(result_image).astype(np.float32), {'name':transform + ' Registration'}

@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return register, {'area': 'bottom'}
