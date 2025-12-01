from typing import TYPE_CHECKING
from magicgui import magic_factory
import itk
from itk_napari_conversion import image_from_image_layer, image_layer_from_image
from pathlib import Path

# For IDE type support and autocompletion
# https://napari.org/stable/guides/magicgui.html?highlight=type_checking
if TYPE_CHECKING:
    import napari

from napari.utils import notifications

def on_init(widget):
    """
    Initializes widget layout.
    Updates widget layout according to user input.
    """
    widget.native.setStyleSheet("QWidget{font-size: 12pt;}")

    widget.interpolation_order.visible = False

    @widget.advanced.changed.connect
    def on_advanced_changed(value):
        widget.interpolation_order.visible = value

    widget.native.layout().addStretch()


@magic_factory(
    widget_init=on_init,
    layout="vertical",
    call_button="transform",
    transform_file={
        "filter": "*.txt;*.toml",
        "tooltip": "Load a transformation parameter file",
    },
    interpolation_order={"min": 0, "max": 5, "tooltip": "Override interpolation order"},
)
def create_transformix_widget(
    image: "napari.layers.Image" = None,
    transform_file: Path = "",
    advanced: bool = False,
    interpolation_order: int = 3,
) -> "napari.layers.Image":

    if not image:
        notifications.show_error("No image selected for transformation")
        return None

    if transform_file == Path():
        notifications.show_error("Select transformation parameter file")
        return None

    # Convert image layer to itk image
    image = image_from_image_layer(image)
    image = image.astype(itk.F)

    # Read transform parameters
    transform_parameter_object = itk.ParameterObject.New()
    transform_parameter_object.ReadParameterFile(str(transform_file))

    # Override interpolation order if 'advanced' is chosen
    if advanced:
        transform_parameter_object.SetParameter(
            0, "ResampleInterpolator", "FinalBSplineInterpolator"
        )
        transform_parameter_object.SetParameter(
            0, "FinalBSplineInterpolationOrder", str(interpolation_order)
        )

    # Call transformix
    result_image_transformix = itk.transformix_filter(image, transform_parameter_object)

    # Convert result (itk.Image) to napari layer
    layer = image_layer_from_image(result_image_transformix)
    layer.name = "transformed image"
    return layer
