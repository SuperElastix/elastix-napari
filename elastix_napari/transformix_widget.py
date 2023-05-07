from typing import TYPE_CHECKING
import elastix_napari.utils as utils
from magicgui import magic_factory
import itk
from itk_napari_conversion import image_from_image_layer, image_layer_from_image
from pathlib import Path

# For IDE type support and autocompletion
# https://napari.org/stable/guides/magicgui.html?highlight=type_checking
if TYPE_CHECKING:
    import napari



def on_init(widget):
    """
    Initializes widget layout.
    Updates widget layout according to user input.
    """
    widget.native.setStyleSheet("QWidget{font-size: 12pt;}")

    setattr(getattr(widget, 'interpolation_order'), 'visible', False)

    @widget.advanced.changed.connect
    def toggle_advanced_widget(value):
        setattr(getattr(widget, 'interpolation_order'), 'visible', value)

    widget.native.layout().addStretch()


@magic_factory(widget_init=on_init, layout='vertical', call_button='transform',
               transform_file={"filter": "*.txt",
                               "tooltip": "Load a transformation parameter file"},
               interpolation_order={'min': 0, 'max': 5,
                                    'tooltip': "Override interpolation order"})
def create_transformix_widget(image: 'napari.layers.Image',
                              transform_file: Path,
                              interpolation_order: int = 3,
                              advanced: bool = False
                              ) -> 'napari.layers.Image':
    
    if not image:
        return utils.error("No image selected for transformation")
    
    if not utils.check_filename(transform_file):
        return utils.error("Select transformation parameter file")

    # Convert image layer to itk image
    image = image_from_image_layer(image)
    image = image.astype(itk.F)

    # Read transform parameters
    transform_parameter_object = itk.ParameterObject.New()
    transform_parameter_object.ReadParameterFile(str(transform_file))

    # Override interpolation order if 'advanced' is chosen
    if advanced:
        transform_parameter_object.SetParameter(0, "ResampleInterpolator", "FinalBSplineInterpolator")
        transform_parameter_object.SetParameter(0, "FinalBSplineInterpolationOrder", str(interpolation_order))

    # Call transformix
    result_image_transformix = itk.transformix_filter(image, transform_parameter_object)

    # Convert result (itk.Image) to napari layer
    layer = image_layer_from_image(result_image_transformix)
    layer.name = "transformed image"
    return layer