from .core import Mode
from datetime import datetime
from arrow import Arrow, ArrowFactory
__all__ = ["near", "before", "after"]


class ApproximateArrow(Arrow):
    _approximate_range = None
    _approximate_mode = None

    @property
    def datetime(self):
        return ApproximateDatetime(self)

    def __eq__(self, other):
        if self._approximate_mode is Mode.Exact:
            return super().__eq__(other)

        if not isinstance(other, (Arrow, datetime)):
            return False
        # Don't use inner _datetime
        return self.datetime == self._get_datetime(other)


class ApproximateDatetime:
    _default_range = {"seconds": 0}
    _default_mode = Mode.Exact

    def __init__(self, arrow):
        self.arrow = arrow

    def __eq__(self, other):
        # Arrow does the heavy lifting with type checks here
        replace_kwargs = dict(getattr(
            self.arrow, "_approximate_range", self._default_range))
        lower = self.arrow.replace(**replace_kwargs)
        upper = self.arrow.replace(**replace_kwargs)

        # Check lower, upper, or both
        mode = getattr(
            self.arrow, "_approximate_mode", self._default_mode)
        if mode is Mode.Before:
            return other < upper
        elif mode is Mode.After:
            return other > lower
        elif mode is Mode.Within:
            return lower < other < upper
        else:
            raise RuntimeError("Unknown approximation mode {}".format(mode))


def after(arrow, **kwargs):
    return _approximate(arrow, Mode.After, **kwargs)


def before(arrow, **kwargs):
    return _approximate(arrow, Mode.Before, **kwargs)


def near(arrow, **kwargs):
    return _approximate(arrow, Mode.Within, **kwargs)


def _approximate(arrow_instance, mode, **kwargs):
    approx = _factory.get(arrow_instance)
    approx._approximate_range = kwargs
    approx._approximate_mode = mode
    return approx
_factory = ArrowFactory(type=ApproximateArrow)
