"""Διεπαφή με την πύλη πληρωμών.

Η πραγματική πύλη είναι εξωτερική υπηρεσία. Το σύστημα εξαρτάται μόνο
από τη διεπαφή PaymentGateway, ώστε στα tests να αντικαθίσταται.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class PaymentResult:
    ok: bool
    ref: str | None = None
    reason: str | None = None


class PaymentGateway(Protocol):
    def authorize(self, amount: Decimal, card_token: str) -> PaymentResult: ...

    def refund(self, ref: str, amount: Decimal) -> bool: ...


class SandboxGateway:
    """Πύλη για επιδείξεις. Απορρίπτει κάρτες με token που αρχίζει από 'declined'."""

    def __init__(self) -> None:
        self._seq = itertools.count(1)
        self.charges: dict[str, Decimal] = {}
        self.refunds: dict[str, Decimal] = {}

    def authorize(self, amount: Decimal, card_token: str) -> PaymentResult:
        if card_token.startswith("declined"):
            return PaymentResult(ok=False, reason="card_declined")
        ref = f"PAY-{next(self._seq):05d}"
        self.charges[ref] = amount
        return PaymentResult(ok=True, ref=ref)

    def refund(self, ref: str, amount: Decimal) -> bool:
        if ref not in self.charges:
            return False
        self.refunds[ref] = amount
        return True
