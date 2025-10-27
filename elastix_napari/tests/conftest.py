#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING, Tuple
from pathlib import Path
import numpy as np
import pytest
import itk
from itk_napari_conversion import image_layer_from_image

if TYPE_CHECKING:
    import napari


############################################################################################
# Implementation from: https://github.com/pytest-dev/pytest/issues/3730#issuecomment-567142496
# Code to remove items from the cartesian product of fixtures e.g. [images_2D, masks_3D]
def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "uncollect_if(*, func): function to unselect tests from parametrization",
    )


def pytest_collection_modifyitems(config, items):
    removed = []
    kept = []
    for item in items:
        m = item.get_closest_marker("uncollect_if")
        if m:
            func = m.kwargs["func"]
            if func(**item.callspec.params):
                removed.append(item)
                continue
        kept.append(item)
    if removed:
        config.hook.pytest_deselected(items=removed)
        items[:] = kept


############################################################################################


@pytest.fixture(scope="session")
def data_dir() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def images_2D(data_dir) -> Tuple["napari.layers.Image", "napari.layers.Image"]:
    fixed_image = itk.imread(str(data_dir / "CT_2D_head_fixed.mha"), itk.F)
    fixed_image = image_layer_from_image(fixed_image)
    moving_image = itk.imread(str(data_dir / "CT_2D_head_moving.mha"), itk.F)
    moving_image = image_layer_from_image(moving_image)
    return (fixed_image, moving_image)


@pytest.fixture(scope="session")
def images_3D(data_dir) -> Tuple["napari.layers.Image", "napari.layers.Image"]:
    # Create a stack of 2D arrays to use as 3D image
    def create_3D_image(filepath):
        image = itk.imread(filepath, itk.F)
        image = np.asarray(image)
        image = np.concatenate(10 * [image[np.newaxis,]])
        image = itk.image_from_array(image)
        image = image_layer_from_image(image)
        return image

    fixed_image = create_3D_image(str(data_dir / "CT_2D_head_fixed.mha"))
    moving_image = create_3D_image(str(data_dir / "CT_2D_head_moving.mha"))
    return (fixed_image, moving_image)


@pytest.fixture(scope="session", params=["images_2D", "images_3D"])
def images(request):
    return request.getfixturevalue(request.param)


# TODO: Make more meaningful masks
@pytest.fixture(scope="session")
def masks_2D() -> Tuple["napari.layers.Image", "napari.layers.Image"]:
    mask = np.zeros([100, 100], np.uint8)
    mask[:90, :100] = 1
    mask = itk.image_view_from_array(mask)
    mask = image_layer_from_image(mask)
    return (mask, mask)


@pytest.fixture(scope="session")
def masks_3D() -> Tuple["napari.layers.Image", "napari.layers.Image"]:
    mask = np.zeros([10, 100, 100], np.uint8)
    mask[:, :90, :100] = 1
    mask = itk.image_view_from_array(mask)
    mask = image_layer_from_image(mask)
    return (mask, mask)


@pytest.fixture(scope="session", params=["masks_2D", "masks_3D"])
def masks(request):
    return request.getfixturevalue(request.param)


@pytest.fixture(scope="session")
def pointsets_2D(data_dir) -> Tuple["Path", "Path"]:
    return (
        data_dir / "fixed_pointset_2D_test.txt",
        data_dir / "moving_pointset_2D_test.txt",
    )


@pytest.fixture(scope="session")
def pointsets_3D(data_dir) -> Tuple["Path", "Path"]:
    return (
        data_dir / "fixed_pointset_3D_test.txt",
        data_dir / "moving_pointset_3D_test.txt",
    )


@pytest.fixture(scope="session", params=["pointsets_2D", "pointsets_3D"])
def pointsets(request):
    return request.getfixturevalue(request.param)


@pytest.fixture(scope="function")
def default_rigid() -> "itk.ParameterObject":
    default_rigid = itk.ParameterObject.New()
    default_rigid.SetParameterMap(default_rigid.GetDefaultParameterMap("rigid"))
    return default_rigid
