import elastix_napari
import pytest

# This is your plugin name declared in your napari.plugins entry point
MY_PLUGIN_NAME = "elastix-napari"

# Names of the widgets
MY_WIDGET_NAMES = ["elastix_registration", "transformix"]


@pytest.mark.parametrize("widget_name", MY_WIDGET_NAMES)
def test_widget_creation(widget_name, make_napari_viewer, napari_plugin_manager):
    viewer = make_napari_viewer()
    num_dw = len(viewer.window._dock_widgets)
    widget = viewer.window.add_plugin_dock_widget(
        plugin_name=MY_PLUGIN_NAME, widget_name=widget_name
    )
    assert len(viewer.window._dock_widgets) == num_dw + 1
