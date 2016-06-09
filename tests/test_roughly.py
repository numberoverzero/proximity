import arrow
import pytest
import uuid
from roughly import near, has_type


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


def test_has_type_matches():
    expected_type = uuid.UUID
    placeholder = has_type(expected_type)
    value = uuid.uuid4()

    assert placeholder == value
    assert value == placeholder


def test_has_type_fails():
    placeholder = has_type(int)
    value = uuid.uuid4()
    assert placeholder != value
    assert value != placeholder
