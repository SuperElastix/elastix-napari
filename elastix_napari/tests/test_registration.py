import pytest
import elastix_napari
import itk
from elastix_napari import elastix_registration
import numpy as np
from qtpy.QtWidgets import QMessageBox
from itk_napari_conversion import image_layer_from_image
from itk_napari_conversion import image_from_image_layer
from pathlib import Path


def get_er(*args, **kwargs):
    er_func = elastix_registration.elastix_registration()
    return er_func(*args, **kwargs)


# Test normal registration
# @pytest.mark.parametrize("fixed_image, moving_image", [(fixed_image_2D, moving_image_2D),])
def test_registration(fixed_image, moving_image):
    result_image = get_er(fixed_image, moving_image, preset='rigid')
    mean_diff = np.absolute(np.subtract(
        np.asarray(image_from_image_layer(result_image)),
        np.asarray(image_from_image_layer(fixed_image)))).mean()
    assert mean_diff < 0.001


# Test Masked registration
def test_masked_registration(fixed_image, moving_image, fixed_mask, moving_mask):
    result_image = get_er(fixed_image, moving_image,
                          fixed_mask=fixed_mask, moving_mask=moving_mask,
                          preset='rigid', masks=True)

    # Filter artifacts out of the images.
    masked_fixed_image = np.asarray(
        image_from_image_layer(fixed_image))[0:90, 0:90]
    masked_result_image = np.asarray(
        image_from_image_layer(result_image))[0:90, 0:90]

    mean_diff = np.absolute(np.subtract(masked_fixed_image,
                                        masked_result_image)).mean()
    assert mean_diff < 0.001


# Test Point set registration
def test_pointset_registration(fixed_image, moving_image, fixed_ps, moving_ps):
    result_image = get_er(fixed_image, moving_image, fixed_ps=fixed_ps,
                          moving_ps=moving_ps, preset='rigid',
                          advanced=True)

    mean_diff = np.absolute(np.subtract(
        np.asarray(image_from_image_layer(result_image)),
        np.asarray(image_from_image_layer(fixed_image)))).mean()
    assert mean_diff < 0.001


# Test registration with custom parameter textfiles
def test_custom_registration(fixed_image, moving_image, data_dir):
    filename = "parameters_Rigid.txt"
    result_image = get_er(fixed_image, moving_image, preset='custom',
                          param1=data_dir / filename,
                          param2=data_dir / filename)

    mean_diff = np.absolute(np.subtract(
        np.asarray(image_from_image_layer(result_image)),
        np.asarray(image_from_image_layer(fixed_image)))).mean()
    assert mean_diff < 0.01


def test_initial_transform(fixed_image, moving_image, data_dir):
    init_trans_filename = "TransformParameters.0.txt"
    result_image = get_er(
        fixed_image, moving_image, preset='rigid',
        init_trans=data_dir / init_trans_filename, resolutions=6,
        max_iterations=500, advanced=True)
    mean_diff = np.absolute(np.subtract(
        np.asarray(image_from_image_layer(result_image)),
        np.asarray(image_from_image_layer(fixed_image)))).mean()
    assert mean_diff < 0.01


def test_empty_images():
    im = get_er(None, None, preset='rigid')
    assert isinstance(im, QMessageBox)


def test_empty_masks(fixed_image, moving_image):
    im = get_er(fixed_image, moving_image, fixed_mask=None, moving_mask=None,
                preset='rigid', masks=True)
    assert isinstance(im, QMessageBox)

def test_empty_output_dir(fixed_image, moving_image):
    im = get_er(fixed_image, moving_image, preset='rigid', save_output=True)
    assert isinstance(im, QMessageBox)

def test_writing_result(fixed_image, moving_image, tmpdir):
    tmpdir = Path(tmpdir)
    im = get_er(fixed_image, moving_image, preset='rigid', save_output=True,
                output_dir=tmpdir)
    assert (tmpdir / "TransformParameters.0.txt").exists()
    


