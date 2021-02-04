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
from magicgui import magicgui
from itk import itkElastixRegistrationMethodPython
import itk

if TYPE_CHECKING:
    from napari.types import ImageData, LabelsData, LayerDataTuple

@magicgui(call_button="register", transform = {"choices": ["rigid", "affine", "bspline"]})
def register(fixed: 'napari.types.ImageData', moving:'napari.types.ImageData', transform: str) -> 'napari.types.LayerDataTuple':
    parameter_object = parameterObject(transform)
    result_image, result_transform_parameters = itk.elastix_registration_method(
        fixed, moving,
        parameter_object=parameter_object,
        log_to_console=True)
    return np.asarray(result_image).astype(np.float32), {'name':transform + ' Registration'}

@napari_hook_implementation
def napari_experimental_provide_function():
    return register
