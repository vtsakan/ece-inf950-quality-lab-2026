"""Ειδοποιήσεις με email (Σ12, Δ3)."""

from __future__ import annotations

import os
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage

from . import store

SMTP_HOST = os.environ.get("STUDYROOM_SMTP", "")
SENDER = "studyroom@library.example.edu"

SENT: list[EmailMessage] = []   # αντίγραφα όσων στάλθηκαν, για έλεγχο


def _send(to, subject, body):
    msg = EmailMessage()
    msg["From"] = SENDER
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    SENT.append(msg)
    if SMTP_HOST:
        with smtplib.SMTP(SMTP_HOST) as smtp:
            smtp.send_message(msg)


def send_confirmation(student, booking):
    if student.lang == "en":
        subject = "StudyRoom: booking confirmed"
        body = f"Room {booking.room_code}, {booking.start:%d/%m %H:%M}, {booking.hours} h."
    else:
        subject = "StudyRoom: επιβεβαίωση κράτησης"
        body = f"Αίθουσα {booking.room_code}, {booking.start:%d/%m %H:%M}, {booking.hours} ώρες."
    _send(student.email, subject, body)


def send_block_notice(student, cancelled):
    if student.lang == "en":
        subject = "StudyRoom: account blocked"
        body = f"Blocked until {student.blocked_until:%d/%m %H:%M}. Cancelled: {len(cancelled)}."
    else:
        subject = "StudyRoom: αποκλεισμός λογαριασμού"
        body = f"Αποκλεισμός έως {student.blocked_until:%d/%m %H:%M}. Ακυρώθηκαν: {len(cancelled)}."
    _send(student.email, subject, body)


def send_reminders():
    """Υπενθύμιση μία ώρα πριν την έναρξη. Καλείται από cron κάθε 10 λεπτά."""
    now = datetime.now()
    count = 0
    for b in store.all_bookings():
        if b.status == "active" and now + timedelta(minutes=50) <= b.start < now + timedelta(minutes=60):
            student = store.get_student(b.student_id)
            if student.lang == "en":
                _send(student.email, "StudyRoom: reminder", f"Room {b.room_code} at {b.start:%H:%M}.")
            else:
                _send(student.email, "StudyRoom: υπενθύμιση", f"Αίθουσα {b.room_code} στις {b.start:%H:%M}.")
            count += 1
    return count
