try:
    from ._version import __version__
except ImportError:  # pragma: no cover
    __version__ = "dev"

from .core import *  # noqa: F403
