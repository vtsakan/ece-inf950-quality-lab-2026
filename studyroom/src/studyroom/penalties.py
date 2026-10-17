"""Χαμένες κρατήσεις και αποκλεισμός (Σ6, Δ2, Δ3)."""

from __future__ import annotations

from datetime import timedelta

from . import notify, rules, store
from .models import ACTIVE, AUTO_CANCELLED, MISSED_STATUSES


def count_missed(student_id, now) -> int:
    """Χαμένες κρατήσεις του φοιτητή στις τελευταίες 30 ημέρες."""
    since = now - timedelta(days=rules.MISSED_WINDOW_DAYS + 1)
    count = 0
    for b in store.bookings_for_student(student_id):
        if b.status in MISSED_STATUSES:
            if b.start >= since:
                count += 1
    return count


def apply_penalties(student_id, now) -> bool:
    """Αποκλείει τον φοιτητή αν συμπλήρωσε 3 χαμένες. Επιστρέφει αν αποκλείστηκε."""
    student = store.get_student(student_id)
    if student is None:
        return False
    if student.blocked_until and student.blocked_until > now:
        return False
    if count_missed(student_id, now) < rules.MISSED_LIMIT:
        return False
    student.blocked_until = now + timedelta(days=rules.BLOCK_DAYS)
    cancelled = []
    for b in store.bookings_for_student(student_id):
        if b.status == ACTIVE and now <= b.start < student.blocked_until:
            b.status = AUTO_CANCELLED
            b.cancelled_at = now
            cancelled.append(b)
    notify.send_block_notice(student, cancelled)
    return True


def unblock(student_id) -> None:
    student = store.get_student(student_id)
    if student is not None:
        student.blocked_until = None
