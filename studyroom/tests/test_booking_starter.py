"""Αρχικά tests της ομάδας ανάπτυξης."""

from datetime import datetime

import pytest

from studyroom import BookingError, create_booking


def test_simple_booking(now):
    b = create_booking("1001", "Α-1", datetime(2026, 11, 4, 10, 0), 1, now=now)
    assert b.status == "active"


def test_group_larger_than_room_is_rejected(now):
    with pytest.raises(BookingError):
        create_booking("1001", "Α-1", datetime(2026, 11, 4, 10, 0), 1, members=["1002", "1003"], now=now)


def test_same_room_same_hour_is_rejected(now):
    create_booking("1001", "Β-1", datetime(2026, 11, 4, 12, 0), 2, now=now)
    with pytest.raises(BookingError):
        create_booking("1002", "Β-1", datetime(2026, 11, 4, 13, 0), 1, now=now)


def test_sunday_is_closed(now):
    with pytest.raises(BookingError):
        create_booking("1001", "Α-1", datetime(2026, 11, 8, 10, 0), 1, now=now)
