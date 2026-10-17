"""Αρχικά δεδομένα για ανάπτυξη και επίδειξη."""

from __future__ import annotations

from . import store
from .models import Room, Student

ROOMS = [
    Room("Α-1", 2), Room("Α-2", 2),
    Room("Β-1", 4, floor=2), Room("Β-2", 4, floor=2),
    Room("Γ-1", 6, floor=2),
    Room("Α-ΙΣ", 4, floor=0, accessible=True),
]

STUDENTS = [
    Student("1001", "Μαρία Π.", "1001@uni.example.edu"),
    Student("1002", "Νίκος Α.", "1002@uni.example.edu"),
    Student("1003", "Elena R.", "1003@uni.example.edu", lang="en"),
    Student("1004", "Γιάννης Κ.", "1004@uni.example.edu", accessibility=True),
    Student("9001", "Υπάλληλος πάγκου", "desk@library.example.edu", role="staff"),
]


def load() -> None:
    for room in ROOMS:
        store.add_room(Room(room.code, room.capacity, room.floor, room.accessible))
    for s in STUDENTS:
        store.add_student(Student(s.id, s.name, s.email, s.lang, s.accessibility, None, s.role))
