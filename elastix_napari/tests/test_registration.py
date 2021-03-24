import pytest
import elastix_napari
import itk
from elastix_napari import elastix_registration
import numpy as np

# Test widget function
def test_dock_widget():
    assert elastix_napari.napari_experimental_provide_dock_widget() != None

# Helper functions
def image_generator(x1, x2, y1, y2, mask=False, artefact=False):
    if mask:
        image = np.zeros([100, 100], np.uint8)
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
    fixed_image = image_generator(25,75,25,75)
    moving_image = image_generator(1,51,10,60)
    result_image = get_er(fixed_image, moving_image, preset='rigid', filenames='data/parameter_Rigid.txt')[0]
    mean_diff = np.absolute(np.subtract(result_image, fixed_image)).mean()
    assert mean_diff < 0.001

# Test Masked registration
def test_masked_registration():
    fixed_image = image_generator(25, 75, 25, 75, artefact=True)
    moving_image = image_generator(1, 51, 10, 60, artefact=True)

    # Create mask for artefact
    fixed_mask = image_generator(0, 100, 0, 90, mask=True)
    moving_mask = image_generator(0, 100, 0, 90, mask=True)
    result_image = get_er(fixed_image, moving_image, fixed_mask, moving_mask, preset='rigid', use_masks=True)[0]
    mean_diff = np.absolute(np.subtract(np.asarray(result_image)[0:100,0:90], np.asarray(fixed_image)[0:100,0:90])).mean()
    assert mean_diff < 0.5

print(test_registration())
print(test_masked_registration())
# print(elastix_registration.elastix_registration()())
