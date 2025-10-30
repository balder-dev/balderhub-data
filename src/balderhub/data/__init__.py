from balderhub.data.lib.utils.decorator_register_for_data_item import register_for_data_item

__all__ = [

    "register_for_data_item",

    "__version__",

    "__version_tuple__",

]

try:
    from ._version import __version__, __version_tuple__
except ImportError:
    __version__ = ""
    __version_tuple__ = tuple()
