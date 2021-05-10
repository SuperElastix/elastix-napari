import pytest
import elastix_napari
import itk
from elastix_napari import elastix_registration
import numpy as np
from qtpy.QtWidgets import QMessageBox


# Test widget function
def test_dock_widget():
    assert elastix_napari.napari_experimental_provide_dock_widget() is not None


# Helper functions
def image_generator(x1, x2, y1, y2, mask=False, artefact=False,
                    pointset=False, ps_name='fixed', data_dir='none'):
    if mask:
        image = np.zeros([100, 100], np.uint8)
    elif pointset:
        # Create fixed point set
        filename = ps_name + "_point_set_test.txt"
        point_set = open(str(data_dir / filename), "w+")
        point_set.write("point\n4\n")
        point_set.write(str(x1) + " " + str(y1) + "\n")
        point_set.write(str(x1) + " " + str(y2) + "\n")
        point_set.write(str(x2) + " " + str(y1) + "\n")
        point_set.write(str(x2) + " " + str(y2) + "\n")
        point_set.close()
        return (str(data_dir / filename), 'x')
    else:
        image = np.zeros([100, 100], np.float32)
    image[y1:y2, x1:x2] = 1
    if artefact:
        image[-10:, :] = 1
    image = itk.image_view_from_array(image)
    return image


def get_er(*args, **kwargs):
    er_func = elastix_registration.elastix_registration()
    return er_func(*args, **kwargs)


# Test normal registration
def test_registration():
    fixed_image = image_generator(25, 75, 25, 75)
    moving_image = image_generator(1, 51, 10, 60)
    result_image = get_er(fixed_image, moving_image, preset='rigid')[0]
    mean_diff = np.absolute(np.subtract(result_image, fixed_image)).mean()
    assert mean_diff < 0.001


# Test Masked registration
def test_masked_registration():
    fixed_image = image_generator(25, 75, 25, 75, artefact=True)
    moving_image = image_generator(1, 51, 10, 60, artefact=True)

    # Create mask for artefact
    fixed_mask = image_generator(0, 100, 0, 90, mask=True)
    moving_mask = image_generator(0, 100, 0, 90, mask=True)

    result_image = get_er(fixed=fixed_image, moving=moving_image,
                          fixed_mask=fixed_mask, moving_mask=moving_mask,
                          preset='rigid', masks=True)[0]

    # Filter artifacts out of the images.
    masked_fixed_image = np.asarray(fixed_image)[0:90, 0:90]
    masked_result_image = result_image[0:90, 0:90]

    mean_diff = np.absolute(np.subtract(masked_fixed_image,
                                        masked_result_image)).mean()
    assert mean_diff < 0.001


# Test Point set registration
def test_pointset_registration(data_dir):
    fixed_image = image_generator(25, 75, 25, 75)
    moving_image = image_generator(1, 51, 10, 60)

    # Create pointsets for artefact
    fixed_ps = image_generator(25, 75, 25, 75, pointset=True, ps_name='fixed',
                               data_dir=data_dir)
    moving_ps = image_generator(1, 51, 10, 60, pointset=True, ps_name='moving',
                                data_dir=data_dir)

    result_image = get_er(fixed_image, moving_image, fixed_ps=fixed_ps,
                          moving_ps=moving_ps, preset='rigid',
                          advanced=True)[0]

    mean_diff = np.absolute(np.subtract(result_image, fixed_image)).mean()
    assert mean_diff < 0.001


# Test registration with custom parameter textfiles
def test_custom_registration(data_dir):
    fixed_image = image_generator(25, 75, 25, 75)
    moving_image = image_generator(1, 51, 10, 60)

    filename = "parameters_Rigid.txt"
    result_image = get_er(fixed_image, moving_image, preset='custom',
                          param1=(str(data_dir / filename), 'x'),
                          param2=(str(data_dir / filename), 'x'))[0]

    mean_diff = np.absolute(np.subtract(result_image, fixed_image)).mean()
    assert mean_diff < 0.01


def test_initial_transform(data_dir):
    fixed_image = image_generator(25, 75, 25, 75)
    moving_image = image_generator(1, 51, 10, 60)

    init_trans_filename = "TransformParameters.0.txt"
    result_image = get_er(
        fixed_image, moving_image, preset='rigid',
        init_trans=(str(data_dir / init_trans_filename), 'x'), resolutions=6,
        max_iterations=500, advanced=True)[0]
    mean_diff = np.absolute(np.subtract(result_image, fixed_image)).mean()
    assert mean_diff < 0.01


def test_empty_images():
    im = get_er(None, None, preset='rigid')
    assert isinstance(im, QMessageBox)


def test_empty_masks():
    fixed_image = image_generator(25, 75, 25, 75)
    moving_image = image_generator(1, 51, 10, 60)
    im = get_er(fixed_image, moving_image, fixed_mask=None, moving_mask=None,
                preset='rigid', masks=True)
    assert isinstance(im, QMessageBox)
