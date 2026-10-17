"""Σύνδεση με τον ιδρυματικό λογαριασμό (Σ11, Π10).

Στην έκδοση 0.1 η υπηρεσία ταυτοποίησης του ιδρύματος δεν είναι ακόμη
διαθέσιμη. Το token έχει τη μορφή "uid:<αριθμός μητρώου>" και γίνεται δεκτό
χωρίς έλεγχο. Η πραγματική σύνδεση έρχεται όταν δοθεί πρόσβαση στην υπηρεσία.
"""

from __future__ import annotations

from . import store
from .models import Student


def current_user(token: str) -> Student | None:
    if not token or not token.startswith("uid:"):
        return None
    return store.get_student(token[4:])
