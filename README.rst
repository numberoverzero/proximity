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

Testing a function that returns ``arrow.now()`` usually looks like this::

    import arrow


    def function_under_test():
        return arrow.now()


    def test_function_returns_now():
        now = arrow.now()
        actual = function_under_test()
        assert now.replace(seconds=-2) <= actual <= now.replace(seconds=2)

It gets worse when you want to check two objects that have a datetime field
that should be approximately equal, but you still want the class's
``__eq__`` to check exact equality.  There's a better way::

    import arrow
    import roughly


    def test_function_returns_now():
        now = roughly.near(arrow.now(), seconds=2)
        assert function_under_test() == now


Motivation
----------

Approximate equality should be handled carefully.  You can introduce subtle
errors when two dates are close by one part of the system, but not close in
another.

Most frequently in testing, however, we'd really like to use the existing
equality-based tests for objects that have datetime attributes, without
patching the system that vends datetimes.

Consider a test that stores an object in a mock database, updating an item
with the current time.  We'd really like to use the helpers provided by
``unittest.mock`` like ``assert_called_once_with`` but that requires us to use
exact values.  We need something that **looks** like equality to another
system.

Without roughly, here's the workaround to ensure a date is nearby.  Note that
all of the other arguments could have been checked with mock's assert calls::

    assert engine.save.call_count == 1
    (item, *_), kwargs = engine.save.call_args
    assert item is key
    assert kwargs["atomic"] is True

    # :( One of the the fields in this object is a datetime, so we can't
    # do an exact match.  We could mock arrow.now() but that's really an
    # implementation detail that we shouldn't need to know.
    condition = Key.until >= arrow.now().replace(seconds=-10)
    assert kwargs["condition"].column is condition.column
    assert kwargs["condition"].value >= condition.value

Here's exactly the same check, but with a ``roughly.near`` datetime for the
condition (the condition being tested is a bloop ConditionalExpression)::

    condition = Key.until >= near(arrow.now(), seconds=5)
    engine.save.assert_called_once_with(key, atomic=True, condition=condition)

The approximate parts of the object are injected into the arguments we expect,
and when the ``unittest.mock`` machinery performs the comparison
``self._call_matcher((args, kwargs)) == self._call_matcher(self.call_args)``
and iterates through the ``(args, kwargs)`` tuples, it will compare the
condition object with our approximate datetime to the actual condition with a
real datetime.  Inside that class's ``__eq__``, it will check
``self.value == other.value`` which holds for our ``ApproximateArrow`` compared
to the actual ``Arrow``.
