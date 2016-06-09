import arrow
from .core import Mode
from . import _arrow

__version__ = "0.0.6"
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


def has_type(some_type):
    """is equal to any object that has the expected type"""
    return MatchType(some_type)


class MatchType:
    def __init__(self, expected_type):
        self.expected_type = expected_type

    def __eq__(self, other):
        return isinstance(other, self.expected_type)
