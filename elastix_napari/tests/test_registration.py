import pytest
import elastix_napari
import itk
from elastix_napari import elastix_registration
import numpy as np
from itk_napari_conversion import image_layer_from_image
from itk_napari_conversion import image_from_image_layer
from pathlib import Path


def get_er(*args, **kwargs):
    er_func = elastix_registration.elastix_registration()
    return er_func(*args, **kwargs)


# See explanation in conftest.py
def uncollect_if(images=None, masks=None, pointsets=None):
    if not pointsets:
        return ("2D" in images) != ("2D" in masks)
    else:
        return ("2D" in images) != ("2D" in pointsets)


def test_registration(images, default_rigid, data_dir):
    fixed_image, moving_image = images
    result_image = get_er(fixed_image, moving_image, preset="rigid")

    reference_result_image, _ = itk.elastix_registration_method(
        image_from_image_layer(fixed_image),
        image_from_image_layer(moving_image),
        parameter_object=default_rigid,
    )

    fixed_filepath = Path(data_dir) / "fixed.nii"
    moving_filepath = Path(data_dir) / "moving.nii"

    fixed_image = image_from_image_layer(fixed_image)
    moving_image = image_from_image_layer(moving_image)

    itk.imwrite(fixed_image, str(fixed_filepath))
    itk.imwrite(moving_image, str(moving_filepath))
    assert np.allclose(image_from_image_layer(result_image), reference_result_image)


# Test masked registration
@pytest.mark.uncollect_if(func=uncollect_if)
def test_masked_registration(images, masks, default_rigid):
    fixed_image, moving_image = images
    fixed_mask, moving_mask = masks
    result_image = get_er(
        fixed_image,
        moving_image,
        fixed_mask=fixed_mask,
        moving_mask=moving_mask,
        preset="rigid",
        use_masks=True,
    )
    reference_result_image, _ = itk.elastix_registration_method(
        image_from_image_layer(fixed_image),
        image_from_image_layer(moving_image),
        fixed_mask=image_from_image_layer(fixed_mask),
        moving_mask=image_from_image_layer(moving_mask),
        parameter_object=default_rigid,
    )

    assert np.allclose(image_from_image_layer(result_image), reference_result_image)


# Test point set registration
@pytest.mark.uncollect_if(func=uncollect_if)
def test_pointset_registration(images, pointsets, default_rigid):
    fixed_image, moving_image = images
    fixed_point_set, moving_point_set = pointsets
    result_image = get_er(
        fixed_image,
        moving_image,
        fixed_point_set=fixed_point_set,
        moving_point_set=moving_point_set,
        preset="rigid",
        use_corresponding_points=True,
        advanced=True,
    )
    default_rigid.SetParameter(
        0, "Registration", "MultiMetricMultiResolutionRegistration"
    )
    default_rigid.SetParameter(
        0,
        "Metric",
        [
            default_rigid.GetParameter(0, "Metric")[0],
            "CorrespondingPointsEuclideanDistanceMetric",
        ],
    )
    reference_result_image, _ = itk.elastix_registration_method(
        image_from_image_layer(fixed_image),
        image_from_image_layer(moving_image),
        parameter_object=default_rigid,
        fixed_point_set_file_name=str(fixed_point_set),
        moving_point_set_file_name=str(moving_point_set),
    )
    assert np.allclose(
        image_from_image_layer(result_image), reference_result_image, atol=0.5
    )


# Test registration with custom parameter textfiles
# TODO: Test multiple parameter files as well
def test_custom_registration(images, data_dir):
    fixed_image, moving_image = images
    filename = "parameters_Rigid.txt"
    result_image = get_er(
        fixed_image, moving_image, preset="custom", parameterfile_1=data_dir / filename
    )

    parameter_object = itk.ParameterObject.New()
    parameter_object.AddParameterFile(str(data_dir / filename))

    reference_result_image, _ = itk.elastix_registration_method(
        image_from_image_layer(fixed_image),
        image_from_image_layer(moving_image),
        parameter_object=parameter_object,
    )
    assert np.allclose(image_from_image_layer(result_image), reference_result_image)


# TODO: This test tests more than one things --> split into two
# TODO: Test that any combination of UI options is depicted correctly in the parameter object
def test_initial_transform(images, default_rigid, data_dir):
    fixed_image, moving_image = images
    if len(fixed_image.data.shape) == 2:
        initial_transform_filename = "TransformParameters.0_2D.txt"
    else:
        initial_transform_filename = "TransformParameters.0_3D.txt"

    resolutions = 3
    max_iterations = 50
    result_image = get_er(
        fixed_image,
        moving_image,
        preset="rigid",
        initial_transform=data_dir / initial_transform_filename,
        resolutions=resolutions,
        max_iterations=max_iterations,
        advanced=True,
    )

    # TODO: Advanced should take default values from the current parameter map
    default_rigid.SetParameter(0, "Metric", "AdvancedMattesMutualInformation")
    default_rigid.SetParameter(0, "MaximumNumberOfIterations", str(max_iterations))
    default_rigid.SetParameter(0, "NumberOfResolutions", str(resolutions))
    default_rigid.SetParameter(0, "NumberOfSpatialSamples", str(512))
    default_rigid.SetParameter(0, "MaximumStepLength", str(1.0))

    reference_result_image, _ = itk.elastix_registration_method(
        image_from_image_layer(fixed_image),
        image_from_image_layer(moving_image),
        parameter_object=default_rigid,
        initial_transform_parameter_file_name=str(
            data_dir / initial_transform_filename
        ),
    )

    diff = image_from_image_layer(result_image)[:] - reference_result_image[:]
    print(diff.min(), diff.max())
    assert np.allclose(image_from_image_layer(result_image), reference_result_image)


def test_empty_images():
    im = get_er(None, None, preset="rigid")
    assert im is None


def test_empty_masks(images):
    fixed_image, moving_image = images
    im = get_er(
        fixed_image,
        moving_image,
        fixed_mask=None,
        moving_mask=None,
        preset="rigid",
        use_masks=True,
    )
    assert im is None

def test_empty_output_directory(images):
    fixed_image, moving_image = images
    im = get_er(fixed_image, moving_image, preset="rigid", save_output_to_disk=True)
    assert im is None

def test_writing_result(images, tmpdir):
    fixed_image, moving_image = images
    tmpdir = Path(tmpdir)
    im = get_er(
        fixed_image,
        moving_image,
        preset="rigid",
        save_output_to_disk=True,
        output_directory=tmpdir,
    )
    assert (tmpdir / "TransformParameters.0.txt").exists()
