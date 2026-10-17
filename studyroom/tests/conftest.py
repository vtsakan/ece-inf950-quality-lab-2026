from datetime import datetime

import pytest

from studyroom import rules, seed, store


@pytest.fixture(autouse=True)
def fresh_store():
    store.reset()
    rules.EXAM_PERIODS.clear()
    seed.load()
    yield
    store.reset()


@pytest.fixture
def now():
    # Τρίτη 3 Νοεμβρίου 2026, 10:00
    return datetime(2026, 11, 3, 10, 0)
