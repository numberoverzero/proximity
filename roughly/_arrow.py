from .core import Mode
from datetime import datetime
from arrow import Arrow, ArrowFactory
__all__ = ["near"]


def _negate(kwargs):
    return {key: -value for key, value in kwargs.items()}


class ApproximateArrow(Arrow):
    def __init__(self, *args, **kwargs):
        self._approximate_mode = Mode.Exact
        self._approximate_range = {}
        super().__init__(*args, **kwargs)

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
    # Is this hacky?  Yep.  On the other hand, it means
    # we don't accidentally return parts of a datetime that were
    # assumed strictly equal (say, someone checks that two dates
    # are within a minute, and then a downstream call assumes
    # that_arrow.datetime.seconds is exactly equal.
    # Instead, big failure message for missing attributes.
    __class__ = datetime

    def __init__(self, arrow):
        self.arrow = arrow

    def __eq__(self, other):
        kwargs = self.arrow._approximate_range
        lower = self.arrow.replace(**_negate(kwargs))._datetime
        upper = self.arrow.replace(**kwargs)._datetime

        # Check lower, upper, or both
        mode = self.arrow._approximate_mode
        if mode is Mode.Within:
            return lower < other < upper
        else:  # pragma: no cover
            raise RuntimeError("Unknown approximation mode {}".format(mode))


def near(arrow, **kwargs):
    return _approximate(arrow, Mode.Within, **kwargs)


def _approximate(arrow_instance, mode, **kwargs):
    approx = _factory.get(arrow_instance)
    approx._approximate_range = kwargs
    approx._approximate_mode = mode
    return approx
_factory = ArrowFactory(type=ApproximateArrow)
