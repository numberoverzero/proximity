.. image:: https://img.shields.io/travis/numberoverzero/roughly/master.svg?style=flat-square
    :target: https://travis-ci.org/numberoverzero/roughly
.. image:: https://img.shields.io/coveralls/numberoverzero/roughly/master.svg?style=flat-square
    :target: https://coveralls.io/github/numberoverzero/roughly
.. image:: https://img.shields.io/pypi/v/roughly.svg?style=flat-square
    :target: https://pypi.python.org/pypi/roughly
.. image:: https://img.shields.io/pypi/status/roughly.svg?style=flat-square
    :target: https://pypi.python.org/pypi/roughly
.. image:: https://img.shields.io/github/issues-raw/numberoverzero/roughly.svg?style=flat-square
    :target: https://github.com/numberoverzero/roughly/issues
.. image:: https://img.shields.io/pypi/l/roughly.svg?style=flat-square
    :target: https://github.com/numberoverzero/roughly/blob/master/LICENSE

``__eq__`` overloading for simpler approximate equality testing

Installation
------------
::

    pip install roughly

Usage
-----

Normally we could check if an arrow date is near another arrow date with::

    import arrow
    now = arrow.now()
    a_fraction_later = arrow.now()
    assert now.replace(seconds=-1) < a_fraction_later < now.replace(seconds=1)

What about when the date is part of two objects that we want to be considered
equal?

::

    class Range:
        def __init__(self, lower, upper):
            self.lower = lower
            self.upper = upper

        def __eq__(self, other):
            return (self.lower == other.lower
                    and self.upper == other.upper)

    now = arrow.now()
    a_fraction_later = arrow.now()
    much_later = now.replace(seconds=5)

    some_range = Range(now, much_later)
    same_range = Range(a_fraction_later, much_later)

    # Just barely not equal!
    assert some_range != same_rage

To check that those are effectively equal, we'd need to do the following:

    class Range:
        def __eq__(self, other):
            near_lower = (self.lower.replace(seconds=-1) < self.other.lower
                          and other.lower < self.lower.replace(seconds=1))
            near_upper = (self.upper.replace(seconds=-1) < self.other.upper
                          and other.upper < self.upper.replace(seconds=1))
            return near_lower and near_upper

There's a better way.  Leave that ``Range.__eq__`` method alone::

    from roughly.arrow import near

    now = arrow.now()
    a_fraction_later = arrow.now()
    much_later = now.replace(seconds=5)

    # Nothing changes here, same pure arrow.Arrow classes
    some_range = Range(now, much_later)

    # Wrap values with roughly, overriding the __eq__ to check intervals
    same_range = Range(near(a_fraction_later, seconds=1), near(much_later))


    # Success!  When Range.__eq__ checks self.lower == other.lower,
    # roughly overrides the arrow.Arrow check with a range check
    assert some_range == same_range
