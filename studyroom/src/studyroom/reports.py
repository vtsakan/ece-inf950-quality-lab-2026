"""Αναφορές για τη βιβλιοθήκη (Π7)."""

from __future__ import annotations

import csv
from datetime import date, timedelta

from . import rules, store
from .models import ACTIVE, CHECKED_IN


def weekly_occupancy(week_start: date) -> dict[str, float]:
    """Ποσοστό ωρών με κράτηση ανά αίθουσα για την εβδομάδα Δευτέρα–Σάββατο."""
    result = {}
    for room in store.all_rooms():
        available = 0
        booked = 0
        for i in range(6):
            day = week_start + timedelta(days=i)
            hours = rules.opening_hours(day)
            if hours is None:
                continue
            available += hours[1] - hours[0]
            for b in store.bookings_for_room(room.code, day):
                if b.status in (ACTIVE, CHECKED_IN) or b.checked_in_at is not None:
                    booked += b.hours
        result[room.code] = round(100 * booked / available, 1) if available else 0.0
    return result


def hourly_grid(room_code: str, day: date) -> dict[int, str]:
    """Κατάσταση κάθε ώρας μιας αίθουσας: free, booked, used."""
    hours = rules.opening_hours(day)
    grid = {}
    if hours is None:
        return grid
    for h in range(hours[0], hours[1]):
        grid[h] = "free"
    for b in store.bookings_for_room(room_code, day):
        for h in range(b.start.hour, b.start.hour + b.hours):
            if b.status == CHECKED_IN:
                grid[h] = "used"
            elif b.status == ACTIVE:
                grid[h] = "booked"
    return grid


def student_day_summary(student_id: str, day: date) -> dict:
    """Ώρες που έχει κρατήσει ο φοιτητής την ημέρα και πόσες του μένουν."""
    student = store.get_student(student_id)
    limit = 2
    if rules.is_exam_period(day) or (student is not None and student.accessibility):
        limit = 3
    total = 0
    for bk in store.bookings_for_student(student_id):
        if bk.status in (ACTIVE, CHECKED_IN):
            if bk.created_at.date() == day:
                total += bk.hours
    return {"student": student_id, "day": day.isoformat(), "used": total, "remaining": max(limit - total, 0)}


def export_week_csv(path: str, week_start: date) -> int:
    rows = 0
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["room", "day", "hour", "state"])
        for room in store.all_rooms():
            for i in range(6):
                day = week_start + timedelta(days=i)
                for hour, state in hourly_grid(room.code, day).items():
                    writer.writerow([room.code, day.isoformat(), hour, state])
                    rows += 1
    return rows
