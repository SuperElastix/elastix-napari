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
def test_registration(fixed_image, moving_image, default_rigid):
    result_image = get_er(fixed_image, moving_image, preset='rigid')

    reference_result_image, _ = itk.elastix_registration_method(image_from_image_layer(fixed_image), 
                                                             image_from_image_layer(moving_image), 
                                                             parameter_object=default_rigid)
    assert np.allclose(image_from_image_layer(result_image), reference_result_image)


# Test Masked registration
def test_masked_registration(fixed_image, moving_image, fixed_mask, moving_mask, default_rigid):
    result_image = get_er(fixed_image, moving_image,
                          fixed_mask=fixed_mask, moving_mask=moving_mask,
                          preset='rigid', masks=True)
    reference_result_image, _ = itk.elastix_registration_method(image_from_image_layer(fixed_image), 
                                                             image_from_image_layer(moving_image),
                                                             fixed_mask=image_from_image_layer(fixed_mask),
                                                             moving_mask=image_from_image_layer(moving_mask),
                                                             parameter_object=default_rigid)

    assert np.allclose(image_from_image_layer(result_image), reference_result_image)


# Test Point set registration
def test_pointset_registration(fixed_image, moving_image, fixed_ps, moving_ps, default_rigid):
    result_image = get_er(fixed_image, moving_image, fixed_ps=fixed_ps,
                          moving_ps=moving_ps, preset='rigid',
                          advanced=True)
    default_rigid.SetParameter(0, "Registration", "MultiMetricMultiResolutionRegistration")
    default_rigid.SetParameter(0, "Metric", [default_rigid.GetParameter(0, "Metric")[0], 
                                             "CorrespondingPointsEuclideanDistanceMetric"])
    reference_result_image, _ = itk.elastix_registration_method(image_from_image_layer(fixed_image), 
                                                             image_from_image_layer(moving_image),
                                                             parameter_object=default_rigid,
                                                             fixed_point_set_file_name=str(fixed_ps),
                                                             moving_point_set_file_name=str(moving_ps))
    assert np.allclose(image_from_image_layer(result_image), reference_result_image, atol=0.5)



# Test registration with custom parameter textfiles
# TODO: Test multiple parameter files as well
def test_custom_registration(fixed_image, moving_image, data_dir):
    filename = "parameters_Rigid.txt"
    result_image = get_er(fixed_image, moving_image, preset='custom',
                          param1=data_dir / filename)

    parameter_object = itk.ParameterObject.New()
    parameter_object.AddParameterFile(str(data_dir / filename))

    reference_result_image, _ = itk.elastix_registration_method(image_from_image_layer(fixed_image), 
                                                             image_from_image_layer(moving_image),
                                                             parameter_object=parameter_object)
    assert np.allclose(image_from_image_layer(result_image), reference_result_image)


# TODO: This test tests more than one things --> split into two
# TODO: Test that any combination of UI options is depicted correctly in the parameter object
def test_initial_transform(fixed_image, moving_image, default_rigid, data_dir):
    init_trans_filename = "TransformParameters.0.txt"
    resolutions = 3
    max_iterations = 50
    result_image = get_er(
        fixed_image, moving_image, preset='rigid',
        init_trans=data_dir / init_trans_filename, resolutions=resolutions,
        max_iterations=max_iterations, advanced=True)
        
    # TODO: Advanced should take default values from the current parameter map
    default_rigid.SetParameter(0, "Metric", "AdvancedMattesMutualInformation")
    default_rigid.SetParameter(0, "MaximumNumberOfIterations", str(max_iterations))
    default_rigid.SetParameter(0, "NumberOfResolutions", str(resolutions))
    default_rigid.SetParameter(0, "NumberOfSpatialSamples", str(512))
    default_rigid.SetParameter(0, "MaximumStepLength", str(1.0))

    reference_result_image, _ = itk.elastix_registration_method(image_from_image_layer(fixed_image), 
                                                             image_from_image_layer(moving_image), 
                                                             parameter_object=default_rigid)
    assert np.allclose(image_from_image_layer(result_image), reference_result_image)


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
    