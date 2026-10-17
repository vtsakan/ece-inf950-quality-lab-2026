"""Κρατήσεις: έλεγχος, δημιουργία, ακύρωση, check-in, χαμένες κρατήσεις."""

from __future__ import annotations

from datetime import datetime, timedelta

from . import notify, rules, store
from .models import (
    ACTIVE,
    CANCELLED,
    CHECKED_IN,
    LATE_CANCEL,
    NO_SHOW,
    Booking,
)
from .penalties import apply_penalties


class BookingError(Exception):
    pass


def validate_booking(student_id, room_code, start, hours, members, now=None):
    """Ελέγχει αν επιτρέπεται η κράτηση. Επιστρέφει None ή το μήνυμα σφάλματος."""
    if now is None:
        now = datetime.now()
    student = store.get_student(student_id)
    room = store.get_room(room_code)
    if student is None:
        return "Άγνωστος φοιτητής"
    if room is None or not room.active:
        return "Η αίθουσα δεν είναι διαθέσιμη"
    if student.blocked_until and student.blocked_until > now:
        return "Ο λογαριασμός είναι σε αποκλεισμό έως " + student.blocked_until.strftime("%d/%m %H:%M")
    if hours < 1 or hours > rules.MAX_BOOKING_HOURS:
        return "Η κράτηση διαρκεί 1 ή 2 ώρες"
    if start.minute != 0 or start.second != 0:
        return "Η κράτηση ξεκινά στην αρχή της ώρας"
    if start < now:
        return "Η ώρα έχει περάσει"
    hours_today = rules.opening_hours(start.date())
    if hours_today is None:
        return "Η βιβλιοθήκη είναι κλειστή"
    else:
        if start.hour < hours_today[0] or start.hour + hours > hours_today[1]:
            return "Εκτός ωραρίου βιβλιοθήκης"
    first, last = rules.booking_window(now)
    if start.date() > last:
        # η αίθουσα προσβασιμότητας ανοίγει για τους δικαιούχους από την Παρασκευή (Υ3)
        if room.code == rules.ACCESSIBLE_ROOM and student.accessibility:
            if now.weekday() >= 4 and start.date() <= last + timedelta(days=7):
                pass
            else:
                return "Οι κρατήσεις για αυτή την ημέρα δεν έχουν ανοίξει"
        else:
            return "Οι κρατήσεις για αυτή την ημέρα δεν έχουν ανοίξει"
    if len(members) + 1 > room.capacity:
        return "Η ομάδα ξεπερνά τη χωρητικότητα της αίθουσας"
    if room.capacity == 6 and len(members) + 1 < 3:
        return "Οι αίθουσες 6 ατόμων δίνονται σε ομάδες τουλάχιστον 3 ατόμων"
    if room.code == rules.ACCESSIBLE_ROOM and not student.accessibility:
        if start.date() > first + timedelta(days=5):
            return "Η αίθουσα Α-ΙΣ δίνεται πρώτα στους δικαιούχους"
    # ημερήσιο όριο ωρών (Σ3, Π2, Υ3)
    limit = 2
    if rules.is_exam_period(start.date()) or student.accessibility:
        limit = 3
    used = 0
    for b in store.bookings_for_student(student_id):
        if b.status in (ACTIVE, CHECKED_IN):
            if b.created_at.date() == start.date():
                used += b.hours
    if used + hours > limit:
        return f"Ξεπερνά το ημερήσιο όριο των {limit} ωρών"
    for b in store.bookings_for_room(room_code, start.date()):
        if b.is_live() and b.overlaps(start, start + timedelta(hours=hours)):
            return "Η αίθουσα είναι ήδη κρατημένη"
    for b in store.bookings_for_student(student_id):
        if b.is_live() and b.overlaps(start, start + timedelta(hours=hours)):
            return "Έχετε ήδη κράτηση αυτή την ώρα"
    return None


def create_booking(student_id, room_code, start, hours=1, members=None, now=None) -> Booking:
    members = members or []
    now = now or datetime.now()
    error = validate_booking(student_id, room_code, start, hours, members, now)
    if error:
        raise BookingError(error)
    booking = Booking(student_id, room_code, start, hours, list(members), created_at=now)
    store.add_booking(booking)
    student = store.get_student(student_id)
    notify.send_confirmation(student, booking)
    return booking


def cancel_booking(booking_id, student_id, now=None) -> Booking:
    """Ακύρωση από τον φοιτητή (Π4, Δ2)."""
    now = now or datetime.now()
    booking = store.get_booking(booking_id)
    if booking is None or booking.student_id != student_id:
        raise BookingError("Δεν βρέθηκε η κράτηση")
    if booking.status != ACTIVE:
        raise BookingError("Η κράτηση δεν μπορεί να ακυρωθεί")
    booking.cancelled_at = now
    if booking.start - now > timedelta(hours=1):
        booking.status = CANCELLED
    else:
        booking.status = LATE_CANCEL
        apply_penalties(student_id, now)
    return booking


def check_in(booking_id, person_id, now=None, by_staff=False) -> Booking:
    """Check-in με QR από μέλος της ομάδας (Δ4) ή από υπάλληλο (Π6)."""
    now = now or datetime.now()
    booking = store.get_booking(booking_id)
    if booking is None:
        raise BookingError("Δεν βρέθηκε η κράτηση")
    if not by_staff and person_id != booking.student_id and person_id not in booking.members:
        raise BookingError("Δεν είστε μέλος της κράτησης")
    if booking.status != ACTIVE:
        raise BookingError("Η κράτηση δεν είναι ενεργή")
    if now < booking.start - timedelta(minutes=10):
        raise BookingError("Πολύ νωρίς για check-in")
    if now >= booking.start + timedelta(minutes=rules.CHECKIN_GRACE_MINUTES):
        raise BookingError("Έληξε το περιθώριο check-in")
    booking.status = CHECKED_IN
    booking.checked_in_at = now
    booking.checked_in_by = person_id
    return booking


def sweep_no_shows(now=None) -> list[Booking]:
    """Τρέχει κάθε λεπτό: σημειώνει ως χαμένες όσες δεν έκαναν check-in (Σ5)."""
    now = now or datetime.now()
    missed = []
    for booking in store.all_bookings():
        if booking.status == ACTIVE and now > booking.start + timedelta(minutes=rules.CHECKIN_GRACE_MINUTES):
            booking.status = NO_SHOW
            missed.append(booking)
    for student_id in {b.student_id for b in missed}:
        apply_penalties(student_id, now)
    return missed


def my_bookings(student_id, now=None) -> list[Booking]:
    now = now or datetime.now()
    upcoming = [b for b in store.bookings_for_student(student_id) if b.end > now and b.is_live()]
    return sorted(upcoming, key=lambda b: b.start)
