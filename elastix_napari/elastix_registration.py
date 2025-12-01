from typing import TYPE_CHECKING
from magicgui import magic_factory
import itk
from pathlib import Path
from itk_napari_conversion import (
    image_from_image_layer,
    image_layer_from_image,
    point_set_from_points_layer,
)

# For IDE type support and autocompletion
# https://napari.org/stable/plugins/building_a_plugin/best_practices.html#don-t-require-napari-if-not-necessary
if TYPE_CHECKING:
    import napari

from napari.utils import notifications

def on_init(widget):
    """
    Initializes widget layout.
    Updates widget layout according to user input.
    """
    widget.native.setStyleSheet("QWidget{font-size: 12pt;}")

    for name in [
        "fixed_mask",
        "moving_mask",
        "parameterfile_1",
        "parameterfile_2",
        "parameterfile_3",
        "fixed_points",
        "fixed_point_set",
        "moving_points",
        "moving_point_set",
        "metric",
        "resolutions",
        "max_iterations",
        "spatial_samples",
        "max_step_length",
        "log_to_file",
        "output_directory",
    ]:
        getattr(widget, name).visible = False

    @widget.use_masks.changed.connect
    def on_use_masks_changed(value):
        for name in ["fixed_mask", "moving_mask"]:
            getattr(widget, name).visible = value

    @widget.preset.changed.connect
    def on_preset_changed(value):
        is_custom_preset = value == "custom"
        widget.advanced.visible = not is_custom_preset

        for name in ["parameterfile_1", "parameterfile_2", "parameterfile_3"]:
            getattr(widget, name).visible = is_custom_preset
        for name in [
            "metric",
            "resolutions",
            "max_iterations",
            "spatial_samples",
            "max_step_length",
        ]:
            getattr(widget, name).visible = (
                widget.advanced.value and not is_custom_preset
            )

    @widget.save_output_to_disk.changed.connect
    def on_save_output_changed(value):
        widget.log_to_file.visible = value
        widget.output_directory.visible = value

    @widget.use_corresponding_points.changed.connect
    def on_use_corresponding_points_changed(value):
        for name in [
            "fixed_points",
            "moving_points",
        ]:
            getattr(widget, name).visible = value

        widget.fixed_point_set.visible = value and widget.fixed_points.value is None
        widget.moving_point_set.visible = value and widget.moving_points.value is None

    @widget.fixed_points.changed.connect
    def on_fixed_points_changed(value):
        widget.fixed_point_set.visible = value is None

    @widget.moving_points.changed.connect
    def on_moving_points_changed(value):
        widget.moving_point_set.visible = value is None

    @widget.advanced.changed.connect
    def on_advanced_changed(value):
        if widget.preset.value != "custom":
            for name in [
                "metric",
                "resolutions",
                "max_iterations",
                "spatial_samples",
                "max_step_length",
            ]:
                getattr(widget, name).visible = value

    widget.native.layout().addStretch()


@magic_factory(
    widget_init=on_init,
    layout="vertical",
    call_button="register",
    preset={
        "choices": ["translation", "rigid", "affine", "bspline", "custom"],
        "tooltip": "Select a preset parameter file or select "
        "the 'custom' option to load a custom one",
    },
    fixed_mask={"bind": None},
    moving_mask={"bind": None},
    fixed_point_set={
        "filter": "*.txt",
        "tooltip": "Load a fixed point set",
    },
    moving_point_set={
        "filter": "*.txt",
        "tooltip": "Load a moving point set",
    },
    parameterfile_1={
        "filter": "*.txt;*.toml",
        "tooltip": "Load a custom parameter file",
    },
    parameterfile_2={
        "filter": "*.txt;*.toml",
        "tooltip": "Optionally load a second custom parameter " "file",
    },
    parameterfile_3={
        "filter": "*.txt;*.toml",
        "tooltip": "Optionally load a third custom parameter " "file",
    },
    metric={
        "choices": [
            "AdvancedMattesMutualInformation",
            "AdvancedNormalizedCorrelation",
            "AdvancedMeanSquares",
        ],
        "tooltip": "Select a metric to use",
    },
    initial_transform={
        "filter": "*.txt;*.toml",
        "tooltip": "Load a initial transform from a .txt or TOML file",
    },
    output_directory={
        "mode": "d",
        "tooltip": "Specify output directory to store the results",
    },
    spatial_samples={
        "max": 8192,
        "step": 256,
        "tooltip": "Select the number of spatial " "samples to use",
    },
)
def elastix_registration(
    fixed_image: "napari.layers.Image" = None,
    moving_image: "napari.layers.Image" = None,
    preset: str = "rigid",
    use_masks: bool = False,
    fixed_mask: "napari.layers.Image" = None,
    moving_mask: "napari.layers.Image" = None,
    parameterfile_1: Path = "",
    parameterfile_2: Path = "",
    parameterfile_3: Path = "",
    save_output_to_disk: bool = False,
    log_to_file: bool = False,
    output_directory: Path = "",
    use_corresponding_points: bool = False,
    fixed_points: "napari.layers.Points" = None,
    fixed_point_set: Path = "",
    moving_points: "napari.layers.Points" = None,
    moving_point_set: Path = "",
    initial_transform: Path = "",
    advanced: bool = False,
    metric: str = "AdvancedMattesMutualInformation",
    resolutions: int = 4,
    max_iterations: int = 500,
    spatial_samples: int = 512,
    max_step_length: float = 1.0,
) -> "napari.layers.Image":
    """
    Takes user input and calls elastix' registration function in itkelastix.
    """
    if fixed_image is None or moving_image is None:
        notifications.show_error("No images selected for registration.")
        return None

    # Convert image layer to itk_image
    fixed_image = image_from_image_layer(fixed_image)
    moving_image = image_from_image_layer(moving_image)
    fixed_image = fixed_image.astype(itk.F)
    moving_image = moving_image.astype(itk.F)

    parameter_object = itk.ParameterObject.New()

    kwargs = {
        "parameter_object": parameter_object,
        "log_to_console": True,
    }

    if initial_transform != Path():
        kwargs["initial_transform_parameter_file_name"] = str(initial_transform)

    if preset == "custom":
        for file_path in [parameterfile_1, parameterfile_2, parameterfile_3]:
            if file_path != Path():
                try:
                    parameter_object.AddParameterFile(str(file_path))
                except:
                    notifications.show_error("Parameter file not found or not valid")
                    return None
            else:
                pass
    else:
        if advanced:
            parameter_map = parameter_object.GetDefaultParameterMap(preset, resolutions)
            parameter_map["Metric"] = [metric]
            parameter_map["MaximumStepLength"] = [str(max_step_length)]
            parameter_map["NumberOfSpatialSamples"] = [str(spatial_samples)]
            parameter_map["MaximumNumberOfIterations"] = [str(max_iterations)]
        else:
            parameter_map = parameter_object.GetDefaultParameterMap(preset, 4)

        if use_corresponding_points:
            parameter_map["Registration"] = ["MultiMetricMultiResolutionRegistration"]
            parameter_map["Metric"] += ("CorrespondingPointsEuclideanDistanceMetric",)

            if fixed_points is None:
                if fixed_point_set == Path():
                    return utils.error("Please specify the fixed points!")
                else:
                    kwargs["fixed_point_set_file_name"] = str(fixed_point_set)
            else:
                if fixed_points.data.size > 0:
                    kwargs["fixed_points"] = point_set_from_points_layer(fixed_points).GetPoints()
                else:
                    return utils.error(
                        "Please make sure the selected layer of fixed points has one or more points!"
                    )

            if moving_points is None:
                if moving_point_set == Path():
                    return utils.error("Please specify the moving points!")
                else:
                    kwargs["moving_point_set_file_name"] = str(moving_point_set)
            else:
                if moving_points.data.size > 0:
                    kwargs["moving_points"] = point_set_from_points_layer(moving_points).GetPoints()
                else:
                    return utils.error(
                        "Please make sure the selected layer of moving points has one or more points!"
                    )

        parameter_object.AddParameterMap(parameter_map)

    args = [fixed_image, moving_image]

    if use_masks:
        if fixed_mask is None and moving_mask is None:
            notifications.show_error("No masks selected for registration")
            return None
        else:
            if fixed_mask:
                fixed_mask = image_from_image_layer(fixed_mask)
                fixed_mask = fixed_mask.astype(itk.UC)
                kwargs["fixed_mask"] = fixed_mask

            if moving_mask:
                moving_mask = image_from_image_layer(moving_mask)
                moving_mask = moving_mask.astype(itk.UC)
                kwargs["moving_mask"] = moving_mask

    if save_output_to_disk:
        if not output_directory.is_dir() or output_directory == Path():
            notifications.show_error("Output directory is not chosen/valid")
            return None

        kwargs["log_to_file"] = log_to_file
        kwargs["output_directory"] = str(output_directory)

    # Run elastix registration
    result_image, result_transform_parameters = itk.elastix_registration_method(
        *args, **kwargs
    )

    # Convert result (itk.Image) to napari layer
    layer = image_layer_from_image(result_image)
    layer.name = preset + " Registration"
    return layer
