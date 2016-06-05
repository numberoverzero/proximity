import arrow
from .core import Mode
from . import _arrow

__version__ = "0.0.5"
__all__ = ["Mode", "near"]


def near(obj, *args, **kwargs):
    if isinstance(obj, arrow.Arrow):
        if args:
            raise ValueError("near(arrow.Arrow) only takes one datetime")
        return _arrow.near(obj, **kwargs)
    else:
        raise NotImplementedError(
            "roughly is still under development - make a request!"
            "  https://github.com/numberoverzero/roughly/issues/new")
