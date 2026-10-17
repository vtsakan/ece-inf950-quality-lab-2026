"""Κανόνες της βιβλιοθήκης: ωράριο, όρια, εξεταστικές, παράθυρο κρατήσεων.

Όλοι οι κανόνες κρατήσεων βρίσκονται σε αυτό το αρχείο, ώστε να αλλάζουν
εύκολα όταν η βιβλιοθήκη αποφασίσει κάτι διαφορετικό.
"""

from __future__ import annotations

import csv
from datetime import date, datetime, timedelta

# Ωράριο (Σ2)
WEEKDAY_HOURS = (8, 22)
SATURDAY_HOURS = (10, 18)

# Όρια (Σ3, Π1, Π2, Υ3)
DAILY_LIMIT = 2
DAILY_LIMIT_EXAM = 3
MAX_BOOKING_HOURS = 2

# Check-in και ποινές (Σ5, Σ6, Δ2, Δ3)
CHECKIN_GRACE_MINUTES = 15
MISSED_LIMIT = 3
MISSED_WINDOW_DAYS = 30
BLOCK_DAYS = 7

# Αίθουσα προσβασιμότητας (Υ3)
ACCESSIBLE_ROOM = "Α-ΙΣ"

EXAM_PERIODS: list[tuple[date, date]] = []


def load_exam_calendar(path: str) -> int:
    """Φορτώνει τις εξεταστικές από CSV με στήλες start,end (Υ10)."""
    EXAM_PERIODS.clear()
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            EXAM_PERIODS.append((date.fromisoformat(row["start"]), date.fromisoformat(row["end"])))
    return len(EXAM_PERIODS)


def is_exam_period(day: date) -> bool:
    return any(start <= day <= end for start, end in EXAM_PERIODS)


def opening_hours(day: date) -> tuple[int, int] | None:
    """Ώρες λειτουργίας της ημέρας ή None αν η βιβλιοθήκη είναι κλειστή."""
    if day.weekday() == 6:
        return None
    if day.weekday() == 5:
        return SATURDAY_HOURS
    return WEEKDAY_HOURS


def week_monday(day: date) -> date:
    return day - timedelta(days=day.weekday())


def booking_window(now: datetime) -> tuple[date, date]:
    """Πρώτη και τελευταία ημέρα για τις οποίες επιτρέπεται κράτηση (Δ1).

    Μέσα στην τρέχουσα εβδομάδα επιτρέπονται κρατήσεις για ελεύθερες ώρες.
    Από τη Δευτέρα 08:00 ανοίγει και η επόμενη εβδομάδα (Δευτέρα–Σάββατο).
    """
    monday = week_monday(now.date())
    opening = datetime.combine(monday, datetime.min.time()).replace(hour=8)
    if now >= opening:
        last = monday + timedelta(days=12)
    else:
        last = monday + timedelta(days=5)
    return now.date(), last
