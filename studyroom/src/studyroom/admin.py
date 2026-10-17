"""Είσοδος αιτημάτων από τη διεπαφή (web και πάγκος βιβλιοθήκης).

Κάθε αίτημα είναι λεξικό με action, user και παραμέτρους. Η απάντηση είναι
λεξικό με ok, message και data, στη γλώσσα του χρήστη.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from . import booking, penalties, reports, rules, store
from .models import Room


def handle(request: dict) -> dict:
    action = request.get("action")
    user = store.get_student(request.get("user", ""))
    lang = user.lang if user else "el"
    if user is None:
        return {"ok": False, "message": "Unknown user" if lang == "en" else "Άγνωστος χρήστης"}
    try:
        if action == "book":
            start = datetime.fromisoformat(request["start"])
            members = request.get("members", [])
            if isinstance(members, str):
                members = [m.strip() for m in members.split(",") if m.strip()]
            b = booking.create_booking(user.id, request["room"], start, int(request.get("hours", 1)), members)
            msg = "Booking confirmed" if lang == "en" else "Η κράτηση καταχωρήθηκε"
            return {"ok": True, "message": msg, "data": {"id": b.id}}
        elif action == "cancel":
            b = booking.cancel_booking(request["booking"], user.id)
            if b.status == "late_cancel":
                msg = "Cancelled (counts as missed)" if lang == "en" else "Ακυρώθηκε (μετράει ως χαμένη)"
            else:
                msg = "Cancelled" if lang == "en" else "Ακυρώθηκε"
            return {"ok": True, "message": msg}
        elif action == "checkin":
            booking.check_in(request["booking"], user.id)
            return {"ok": True, "message": "Checked in" if lang == "en" else "Έγινε check-in"}
        elif action == "staff_checkin":
            if user.role != "staff":
                return {"ok": False, "message": "Forbidden" if lang == "en" else "Δεν επιτρέπεται"}
            booking.check_in(request["booking"], user.id, by_staff=True)
            return {"ok": True, "message": "Checked in by staff" if lang == "en" else "Check-in από υπάλληλο"}
        elif action == "my_bookings":
            items = [
                {"id": b.id, "room": b.room_code, "start": b.start.isoformat(), "hours": b.hours}
                for b in booking.my_bookings(user.id)
            ]
            return {"ok": True, "message": "", "data": items}
        elif action == "free_slots":
            day = date.fromisoformat(request["day"])
            if day.weekday() == 6:
                return {"ok": True, "message": "Closed" if lang == "en" else "Κλειστά", "data": {}}
            if day.weekday() == 5:
                first_hour, last_hour = 10, 18
            else:
                first_hour, last_hour = 8, 22
            free = {}
            for room in store.all_rooms():
                if not room.active:
                    continue
                taken = set()
                for b in store.bookings_for_room(room.code, day):
                    if b.status in ("active", "checked_in"):
                        for h in range(b.start.hour, b.start.hour + b.hours):
                            taken.add(h)
                free[room.code] = [h for h in range(first_hour, last_hour) if h not in taken]
            return {"ok": True, "message": "", "data": free}
        elif action == "add_room":
            if user.role != "staff":
                return {"ok": False, "message": "Forbidden" if lang == "en" else "Δεν επιτρέπεται"}
            capacity = int(request["capacity"])
            if capacity not in (2, 4, 6):
                return {"ok": False, "message": "Capacity must be 2, 4 or 6" if lang == "en" else "Χωρητικότητα 2, 4 ή 6"}
            store.add_room(Room(request["code"], capacity, int(request.get("floor", 1)), bool(request.get("accessible"))))
            return {"ok": True, "message": "Room added" if lang == "en" else "Η αίθουσα προστέθηκε"}
        elif action == "disable_room":
            if user.role != "staff":
                return {"ok": False, "message": "Forbidden" if lang == "en" else "Δεν επιτρέπεται"}
            room = store.get_room(request["code"])
            if room is None:
                return {"ok": False, "message": "No such room" if lang == "en" else "Δεν υπάρχει η αίθουσα"}
            room.active = False
            return {"ok": True, "message": "Room disabled" if lang == "en" else "Η αίθουσα απενεργοποιήθηκε"}
        elif action == "unblock":
            if user.role != "staff":
                return {"ok": False, "message": "Forbidden" if lang == "en" else "Δεν επιτρέπεται"}
            penalties.unblock(request["student"])
            return {"ok": True, "message": "Unblocked" if lang == "en" else "Ο αποκλεισμός άρθηκε"}
        elif action == "report":
            if user.role != "staff":
                return {"ok": False, "message": "Forbidden" if lang == "en" else "Δεν επιτρέπεται"}
            week = date.fromisoformat(request["week"])
            week = week - timedelta(days=week.weekday())
            return {"ok": True, "message": "", "data": reports.weekly_occupancy(week)}
        elif action == "load_calendar":
            if user.role != "staff":
                return {"ok": False, "message": "Forbidden" if lang == "en" else "Δεν επιτρέπεται"}
            n = rules.load_exam_calendar(request["path"])
            return {"ok": True, "message": f"{n} periods" if lang == "en" else f"{n} περίοδοι"}
        else:
            return {"ok": False, "message": "Unknown action" if lang == "en" else "Άγνωστη ενέργεια"}
    except booking.BookingError as e:
        return {"ok": False, "message": str(e)}
    except (KeyError, ValueError):
        return {"ok": False, "message": "Bad request" if lang == "en" else "Λάθος αίτημα"}
