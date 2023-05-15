from typing import TYPE_CHECKING
import elastix_napari.utils as utils
from magicgui import magic_factory
import itk
from pathlib import Path
from itk_napari_conversion import image_from_image_layer
from itk_napari_conversion import image_layer_from_image

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

    for x in ['fixed_mask', 'moving_mask', 'param1', 'param2', 'param3',
              'fixed_ps', 'moving_ps', 'metric', 'init_trans',
              'resolutions', 'max_iterations', 'nr_spatial_samples',
              'max_step_length', 'output_dir']:
        setattr(getattr(widget, x), 'visible', False)

    @widget.masks.changed.connect
    def toggle_mask_widgets(value):
        for x in ['fixed_mask', 'moving_mask']:
            setattr(getattr(widget, x), 'visible', value)

    @widget.preset.changed.connect
    def toggle_preset_widget(value):
        if value == "custom":
            for x in ['param1', 'param2', 'param3']:
                setattr(getattr(widget, x), 'visible', True)
            for y in ['metric', 'resolutions', 'max_iterations',
                      'nr_spatial_samples', 'max_step_length']:
                setattr(getattr(widget, y), 'visible', False)

        else:
            for x in ['param1', 'param2', 'param3']:
                setattr(getattr(widget, x), 'visible', False)
            for x in ['metric', 'init_trans', 'resolutions', 'max_iterations',
                      'nr_spatial_samples', 'max_step_length', 'moving_ps',
                      'fixed_ps']:
                setattr(getattr(widget, x), 'visible', widget.advanced.value)

    @widget.save_output.changed.connect
    def toggle_save_output_widget(value):
        setattr(getattr(widget, 'output_dir'), 'visible', value)


    @widget.advanced.changed.connect
    def toggle_advanced_widget(value):
        if widget.preset.value == "custom":
            for x in ['init_trans', 'fixed_ps', 'moving_ps']:
                setattr(getattr(widget, x), 'visible', value)
        else:
            for x in ['metric', 'init_trans', 'resolutions',
                      'max_iterations', 'nr_spatial_samples',
                      'max_step_length', 'fixed_ps', 'moving_ps']:
                setattr(getattr(widget, x), 'visible', value)

    widget.native.layout().addStretch()


@magic_factory(widget_init=on_init, layout='vertical', call_button="register",
               preset={"choices": ["rigid", "affine", "bspline", "custom"],
                       "tooltip": "Select a preset parameter file or select "
                       "the 'custom' option to load a custom one"},
               fixed_mask={'bind': None}, moving_mask={'bind': None},
               fixed_ps={"label": "fixed point set", "filter": "*.txt",
                         "tooltip": "Load a fixed point set"},
               moving_ps={"label": "moving point set", "filter": "*.txt",
                          "tooltip": "Load a moving point set"},
               param1={"label": "parameterfile 1", "filter": "*.txt",
                       "tooltip": 'Load a custom parameter file'},
               param2={"label": "parameterfile 2", "filter": "*.txt",
                       "tooltip": 'Optionally load a second custom parameter '
                       'file'},
               param3={"label": "parameterfile 3", "filter": "*.txt",
                       "tooltip": 'Optionally load a third custom parameter '
                       'file'},
               metric={"choices": ["AdvancedMattesMutualInformation",
                                   "AdvancedNormalizedCorrelation",
                                   "AdvancedMeanSquares"],
                       "tooltip": 'Select a metric to use'},
               init_trans={"label": "initial transform", "filter": "*.txt",
                           "tooltip": 'Load a initial transform from a .txt '
                           'file'},
               output_dir={"label": "output directory", "mode": "d",
                           "tooltip": "Specify output directory to store the results"},
               nr_spatial_samples={"max": 8192, "step": 256,
                                   "tooltip": 'Select the number of spatial '
                                   'samples to use'})
def elastix_registration(fixed_image: 'napari.layers.Image',
                         moving_image: 'napari.layers.Image', preset: str,
                         fixed_mask: 'napari.layers.Image',
                         moving_mask: 'napari.layers.Image',
                         fixed_ps: Path, moving_ps: Path,
                         param1: Path, param2: Path,
                         param3: Path, init_trans: Path,
                         output_dir: Path,
                         metric: str = "AdvancedMattesMutualInformation",
                         resolutions: int = 4, max_iterations: int = 500,
                         nr_spatial_samples: int = 512,
                         max_step_length: float = 1.0,   
                         masks: bool = False, save_output: bool = False, 
                         advanced: bool = False
                         ) -> 'napari.layers.Image':
    """
    Takes user input and calls elastix' registration function in itkelastix.
    """
    if fixed_image is None or moving_image is None:
        return utils.error("No images selected for registration.")
    if fixed_ps.exists() != moving_ps.exists():
        return utils.error("Select both fixed and moving point set.")

    if not utils.check_filename(init_trans):
        init_trans = ''
    if not utils.check_filename(fixed_ps):
        fixed_ps = ''
    if not utils.check_filename(moving_ps):
        moving_ps = ''

    # Convert image layer to itk_image
    fixed_image = image_from_image_layer(fixed_image)
    moving_image = image_from_image_layer(moving_image)
    fixed_image = fixed_image.astype(itk.F)
    moving_image = moving_image.astype(itk.F)

    parameter_object = itk.ParameterObject.New()
    if preset == "custom":
        for par in [param1, param2, param3]:
            if par.suffix == ".txt":
                try:
                    parameter_object.AddParameterFile(str(par))
                except:
                    return utils.error("Parameter file not found or not valid")
            else:
                pass
    else:
        if advanced:
            parameter_map = \
                parameter_object.GetDefaultParameterMap(preset, resolutions)
            parameter_map['Metric'] = [metric]
            if str(fixed_ps) != '' and str(moving_ps) != '':
                parameter_map['Registration'] = [
                    'MultiMetricMultiResolutionRegistration']
                original_metric = parameter_map['Metric']
                parameter_map['Metric'] = \
                    [original_metric[0],
                        'CorrespondingPointsEuclideanDistanceMetric']
            parameter_map['MaximumStepLength'] = [str(max_step_length)]
            parameter_map['NumberOfSpatialSamples'] = [str(nr_spatial_samples)]
            parameter_map['MaximumNumberOfIterations'] = [str(max_iterations)]
        else:
            parameter_map = parameter_object.GetDefaultParameterMap(preset, 4)
        parameter_object.AddParameterMap(parameter_map)

    args = [fixed_image, moving_image]

    kwargs = {"parameter_object": parameter_object,
              "fixed_point_set_file_name": str(fixed_ps),
              "moving_point_set_file_name": str(moving_ps),
              "initial_transform_parameter_file_name": str(init_trans),
              "log_to_console": True}

    if masks:
        if fixed_mask is None and moving_mask is None:
            return utils.error("No masks selected for registration")
        else:
            if fixed_mask:
                fixed_mask = image_from_image_layer(fixed_mask)
                fixed_mask = fixed_mask.astype(itk.UC)
                kwargs["fixed_mask"] = fixed_mask

            if moving_mask:
                moving_mask = image_from_image_layer(moving_mask)
                moving_mask = moving_mask.astype(itk.UC)
                kwargs["moving_mask"] = moving_mask
    
    if save_output:
        if not output_dir.is_dir() or output_dir == Path():
            return utils.error("Output directory is not chosen/valid")

        kwargs["output_directory"] = str(output_dir)            


    # Run elastix registration
    result_image, result_transform_parameters = itk.elastix_registration_method(*args, **kwargs)
    
    # Convert result (itk.Image) to napari layer
    layer = image_layer_from_image(result_image)
    layer.name = preset + " Registration"
    return layer


