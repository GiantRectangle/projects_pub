import create_estimate as ce
import pytest

def test_some_func()
    assert ce.some_func(some_value) == 'boo'

def test_value_error():
    with pytest.raises(ValueError):
        ce.some_func(some_other_value)