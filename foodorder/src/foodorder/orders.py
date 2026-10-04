"""Παραγγελία και μεταβάσεις κατάστασης.

Κανόνας ακύρωσης (FR-11): ο πελάτης ακυρώνει μόνο πριν το εστιατόριο
αποδεχτεί την παραγγελία. Η επιστροφή χρημάτων γίνεται στο ίδιο μέσο πληρωμής.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


class Status(Enum):
    SUBMITTED = "υποβλήθηκε"
    ACCEPTED = "αποδεκτή"
    PREPARING = "σε προετοιμασία"
    DISPATCHED = "εστάλη"
    DELIVERED = "παραδόθηκε"
    CANCELLED = "ακυρώθηκε"


TRANSITIONS: dict[Status, set[Status]] = {
    Status.SUBMITTED: {Status.ACCEPTED, Status.CANCELLED},
    Status.ACCEPTED: {Status.PREPARING, Status.CANCELLED},
    Status.PREPARING: {Status.DISPATCHED},
    Status.DISPATCHED: {Status.DELIVERED},
    Status.DELIVERED: set(),
    Status.CANCELLED: set(),
}


class InvalidTransitionError(Exception):
    pass


_order_ids = itertools.count(1)


@dataclass
class Order:
    total: Decimal
    payment_ref: str
    lines: list[tuple[str, int, Decimal]]
    id: str = field(default_factory=lambda: f"ORD-{next(_order_ids):05d}")
    status: Status = Status.SUBMITTED
    history: list[Status] = field(default_factory=lambda: [Status.SUBMITTED])

    def _move(self, target: Status) -> None:
        if target not in TRANSITIONS[self.status]:
            raise InvalidTransitionError(f"{self.status.name} -> {target.name}")
        self.status = target
        self.history.append(target)

    # Ενέργειες εστιατορίου και διανομέα
    def accept(self) -> None:
        self._move(Status.ACCEPTED)

    def start_preparing(self) -> None:
        self._move(Status.PREPARING)

    def dispatch(self) -> None:
        self._move(Status.DISPATCHED)

    def deliver(self) -> None:
        self._move(Status.DELIVERED)

    # Ενέργεια πελάτη
    def cancel_by_customer(self, gateway) -> bool:
        """Ακυρώνει και ζητά επιστροφή. Επιστρέφει αν η επιστροφή έγινε δεκτή."""
        if self.status not in (Status.SUBMITTED, Status.ACCEPTED):
            raise InvalidTransitionError(f"Ακύρωση από {self.status.name}")
        self._move(Status.CANCELLED)
        return gateway.refund(self.payment_ref, self.total)
