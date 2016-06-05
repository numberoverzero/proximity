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

To check that those are effectively equal, we'd need to do the following::

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
    same_range = Range(near(a_fraction_later, seconds=1), near(much_later, seconds=1))


    # Success!  When Range.__eq__ checks self.lower == other.lower,
    # roughly overrides the arrow.Arrow check with a range check
    assert some_range == same_range

Motivation
----------

For the most part, approximate equality should be handled carefully.  That is,
there are subtle errors lurking when two dates, for example, are said to be the
same, for some window.  Perhaps one section of code may check that they're
"equal" within a minute, while a downstream service expects that validation has
ensures dates are within a second; suddenly there's skew.

Most frequently in testing, however, we'd really like to use equality-based
comparison with values like floats or dates, that are hard to use.

For example, consider a system that calls a mocked database engine, updating
an item with the current time.  We'd really like to use the fantastic helpers
provided by ``unittest.mock``, like ``assert_called_once_with`` but that needs
exact values.

Here's the workaround without roughly, to ensure a date is nearby, while all
other arguments *could* have been checked with mock's assert calls::

    assert engine.save.call_count == 1
    (item, *_), kwargs = engine.save.call_args
    # Known value, perfectly fine with assert_called_once_with
    assert item is key
    # Known value, perfectly fine with assert_called_once_with
    assert kwargs["atomic"] is True
    # :( One of the the fields in this object is a datetime, so we can't
    # do an exact match.  We could mock arrow.now() but that's really an
    # implementation detail that we shouldn't need to know.
    assert kwargs["condition"].column is Key.until
    assert kwargs["condition"].value >= arrow.now().replace(seconds=-1)

Here's exactly the same check, but with a ``roughly.near`` datetime for the
condition (the condition being tested is a bloop ConditionalExpression)::

    condition = Key.until >= near(arrow.now(), seconds=5)
    engine.save.assert_called_once_with(key, atomic=True, condition=condition)

The approximate parts of the object are injected into the arguments we expect,
and when the ``unittest.mock`` machinery eventually gets to comparing its
``self._call_matcher((args, kwargs)) == self._call_matcher(self.call_args)``
the eventual ``==`` decent into the expected kwarg "condition" will check the
actual ``arrow.Arrow`` from the intercepted call's kwargs against the expected
``roughly._arrow.ApproximateArrow`` that we constructed.
