import pytest
import itk
import numpy as np
from elastix_napari import transformix_widget
from itk_napari_conversion import image_from_image_layer
from qtpy.QtWidgets import QMessageBox
from pathlib import Path

def test_transformation(fixed_image, moving_image, default_rigid, tmpdir):
    result_image_elx, result_transform_parameters = itk.elastix_registration_method(image_from_image_layer(fixed_image),
                                                                                    image_from_image_layer(moving_image),
                                                                                    parameter_object=default_rigid,
                                                                                    output_directory=str(tmpdir)
                                                                                    )

    result_image_trx = transformix_widget.create_transformix_widget()(image=moving_image, 
                                                                      transform_file=Path(tmpdir) / "TransformParameters.0.txt")
    
    result_image_elx = np.asarray(result_image_elx)
    result_image_trx = np.asarray(image_from_image_layer(result_image_trx))

    assert np.allclose(result_image_elx, result_image_trx)


def test_empty_image(data_dir):
    result = transformix_widget.create_transformix_widget()(image=None, transform_file=data_dir / "TransformParameters.0.txt")
    assert isinstance(result, QMessageBox)


def test_empty_transform_file(moving_image):
    result = transformix_widget.create_transformix_widget()(image=image_from_image_layer(moving_image), transform_file=Path())
    assert isinstance(result, QMessageBox)


    



