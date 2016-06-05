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
