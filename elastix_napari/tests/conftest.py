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


@pytest.fixture(scope="session")
def data_dir() -> Path:
    return Path(__file__).parent / "data"

@pytest.fixture(scope="session")
# def fixed_image_2D() -> 'napari.layers.Image':
def fixed_image(data_dir) -> 'napari.layers.Image':
    image = itk.imread(str(data_dir / "CT_2D_head_fixed.mha"), itk.F)
    image = image_layer_from_image(image)
    return image

@pytest.fixture(scope="session")
# def moving_image_2D() -> 'napari.layers.Image':
def moving_image(data_dir) -> 'napari.layers.Image':
    image = itk.imread(str(data_dir / "CT_2D_head_moving.mha"), itk.F)
    image = image_layer_from_image(image)
    return image

#TODO: Improve mask fixtures
@pytest.fixture(scope="session")
def fixed_mask() -> 'napari.layers.Image':
    mask = np.zeros([100, 100], np.uint8)
    mask[:90, :100] = 1
    mask = itk.image_view_from_array(mask)
    return image_layer_from_image(mask)    

@pytest.fixture(scope="session")
def moving_mask() -> 'napari.layers.Image':
    mask = np.zeros([100, 100], np.uint8)
    mask[:90, :100] = 1
    mask = itk.image_view_from_array(mask)
    return image_layer_from_image(mask)    

@pytest.fixture(scope="session")
def fixed_ps(data_dir) -> 'Path':
    return data_dir / "fixed_point_set_test.txt"

@pytest.fixture(scope="session")
def moving_ps(data_dir) -> 'Path':
    return data_dir / "moving_point_set_test.txt"

@pytest.fixture(scope="function")
def default_rigid() -> 'itk.ParameterObject':
    default_rigid = itk.ParameterObject.New()
    default_rigid.SetParameterMap(default_rigid.GetDefaultParameterMap('rigid'))
    return default_rigid