import arrow
from roughly._arrow import near, ApproximateArrow


def test_wrong_type():
    invalid = "some-string, not a date"
    approx = near(arrow.now(), minutes=1)
    assert approx != invalid


def test_exact():
    now = arrow.now()
    # Default compare is exact
    approximate = arrow.ArrowFactory(type=ApproximateArrow).get(now)

    assert now == approximate
    assert now.replace(seconds=1) != approximate


def check(approx, equal, not_equal):
    # Using arrow.Arrow
    assert approx == equal
    assert approx != not_equal

    assert equal == approx
    assert not_equal != approx

    # Using approx.datetime
    assert approx.datetime == equal
    assert approx.datetime != not_equal
    assert equal == approx.datetime
    assert not_equal != approx.datetime

    # Using other.datetime
    assert approx == equal.datetime
    assert approx != not_equal.datetime
    assert equal.datetime == approx
    assert not_equal.datetime != approx

    # Both using datetime
    assert approx.datetime == equal.datetime
    assert approx.datetime != not_equal.datetime
    assert equal.datetime == approx.datetime
    assert not_equal.datetime != approx.datetime


def test_near():
    now = arrow.now()
    # only 1 minute away
    nearby = now.replace(minutes=1)
    # too far away
    far = now.replace(minutes=3)

    # within 2 minutes will evaluate as equal
    approx = near(now, minutes=2)
    check(approx, nearby, far)


def test_both_approximate():
    """When both are approximate, both get a chance to say they're equal"""
    now = arrow.now()
    later = now.replace(seconds=20)

    #            now           later
    # |-10|-----|0|-----|10|-----|20|---------------|50|
    #    |---- first -----|
    #    |--------------------- second ---------------|
    first = near(now, seconds=10)
    second = near(later, seconds=30)

    # While first doesn't think second is near,
    # second DOES think first is near.
    assert first == second
    assert second == first
