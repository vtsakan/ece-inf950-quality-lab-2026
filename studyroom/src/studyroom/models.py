"""Οντότητες του StudyRoom: αίθουσες, φοιτητές, κρατήσεις."""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# Καταστάσεις κράτησης
ACTIVE = "active"
CHECKED_IN = "checked_in"
CANCELLED = "cancelled"            # ακύρωση εγκαίρως, δεν μετράει
LATE_CANCEL = "late_cancel"        # ακύρωση λιγότερο από 1 ώρα πριν, μετράει ως χαμένη
NO_SHOW = "no_show"                # δεν έγινε check-in, μετράει ως χαμένη
AUTO_CANCELLED = "auto_cancelled"  # ακυρώθηκε λόγω αποκλεισμού

MISSED_STATUSES = (LATE_CANCEL, NO_SHOW)


@dataclass
class Room:
    code: str
    capacity: int
    floor: int = 1
    accessible: bool = False
    active: bool = True


@dataclass
class Student:
    id: str
    name: str
    email: str
    lang: str = "el"
    accessibility: bool = False   # εγγεγραμμένος στο γραφείο προσβασιμότητας
    blocked_until: datetime | None = None
    role: str = "student"         # student ή staff


_booking_ids = itertools.count(1)


@dataclass
class Booking:
    student_id: str
    room_code: str
    start: datetime
    hours: int
    members: list[str]
    created_at: datetime
    id: str = field(default_factory=lambda: f"BK-{next(_booking_ids):05d}")
    status: str = ACTIVE
    checked_in_at: datetime | None = None
    checked_in_by: str | None = None
    cancelled_at: datetime | None = None

    @property
    def end(self) -> datetime:
        return self.start + timedelta(hours=self.hours)

    def overlaps(self, start: datetime, end: datetime) -> bool:
        return self.start < end and start < self.end

    def is_live(self) -> bool:
        return self.status in (ACTIVE, CHECKED_IN)
