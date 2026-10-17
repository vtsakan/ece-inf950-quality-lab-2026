"""Αποθήκευση στη μνήμη.

Στην έκδοση 0.1 τα δεδομένα κρατιούνται σε λεξικά. Η μεταφορά σε βάση
δεδομένων είναι για την έκδοση 0.3.
"""

from __future__ import annotations

from datetime import date

from .models import Booking, Room, Student

_DB: dict = {"rooms": {}, "students": {}, "bookings": {}}


def reset() -> None:
    for table in _DB.values():
        table.clear()


def add_room(room: Room) -> None:
    _DB["rooms"][room.code] = room


def get_room(code: str) -> Room | None:
    return _DB["rooms"].get(code)


def all_rooms() -> list[Room]:
    return list(_DB["rooms"].values())


def add_student(student: Student) -> None:
    _DB["students"][student.id] = student


def get_student(student_id: str) -> Student | None:
    return _DB["students"].get(student_id)


def add_booking(booking: Booking) -> None:
    _DB["bookings"][booking.id] = booking


def get_booking(booking_id: str) -> Booking | None:
    return _DB["bookings"].get(booking_id)


def all_bookings() -> list[Booking]:
    return list(_DB["bookings"].values())


def bookings_for_room(code: str, day: date) -> list[Booking]:
    return [b for b in _DB["bookings"].values() if b.room_code == code and b.start.date() == day]


def bookings_for_student(student_id: str) -> list[Booking]:
    return [b for b in _DB["bookings"].values() if b.student_id == student_id]
