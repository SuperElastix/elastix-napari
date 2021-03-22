try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

__author__ = "Viktor van der Valk"
__email__ = "v.o.van_der_valk@lumc.nl"

from .elastix_registration import napari_experimental_provide_dock_widget
