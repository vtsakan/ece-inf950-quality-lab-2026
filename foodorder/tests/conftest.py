import pytest

from foodorder import Cart


@pytest.fixture
def cart():
    return Cart()
