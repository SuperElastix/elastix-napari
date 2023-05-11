#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING
from pathlib import Path
import numpy as np
import pytest
import itk
from itk_napari_conversion import image_layer_from_image

if TYPE_CHECKING:
    import napari


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
        return data_dir / filename
    else:
        image = np.zeros([100, 100], np.float32)
    image[y1:y2, x1:x2] = 1
    if artefact:
        image[-10:, :] = 1
    image = itk.image_view_from_array(image)
    image = image_layer_from_image(image)
    return image


@pytest.fixture(scope="session")
def data_dir() -> Path:
    return Path(__file__).parent / "data"

@pytest.fixture(scope="session")
# def fixed_image_2D() -> 'napari.layers.Image':
def fixed_image() -> 'napari.layers.Image':
    return image_generator(25, 75, 25, 75)

@pytest.fixture(scope="session")
# def moving_image_2D() -> 'napari.layers.Image':
def moving_image() -> 'napari.layers.Image':
    return image_generator(1, 51, 10, 60)

@pytest.fixture(scope="session")
def fixed_mask() -> 'napari.layers.Image':
    return image_generator(0, 100, 0, 90, mask=True)

@pytest.fixture(scope="session")
def moving_mask() -> 'napari.layers.Image':
    return image_generator(0, 100, 0, 90, mask=True)

@pytest.fixture(scope="session")
def fixed_ps(data_dir) -> 'Path':
    return image_generator(25, 75, 25, 75, pointset=True, ps_name='fixed',
                               data_dir=data_dir)

@pytest.fixture(scope="session")
def moving_ps(data_dir) -> 'Path':
    return image_generator(1, 51, 10, 60, pointset=True, ps_name='moving',
                                data_dir=data_dir)

