import arrow
import pytest
from roughly import near


def test_near_arrow():
    now = arrow.now()
    not_now = now.replace(seconds=1)
    roughly_now = near(not_now, seconds=5)
    assert roughly_now == now


def test_near_arrow_args():
    """_arrow.near only takes one positional arg"""
    with pytest.raises(ValueError):
        near(arrow.now(), "extra posarg")


def test_not_implemented():
    obj = object()
    with pytest.raises(NotImplementedError) as excinfo:
        near(obj)
    new_issue_url = "https://github.com/numberoverzero/roughly/issues/new"
    assert new_issue_url in str(excinfo.value)
