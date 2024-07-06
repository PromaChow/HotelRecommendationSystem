# test_dummy_code.py
# coverage run -m pytest -q tests/test_dummy_code.py
# coverage report --show-missing --include=dummy_code.py --omit=/tests/

import pytest
from src.dummy_code import add, subtract

def test_add():
    assert add(3, 5) == 8
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_subtract():
    assert subtract(10, 2) == 8
    assert subtract(-1, -1) == 0
    assert subtract(0, 0) == 0
