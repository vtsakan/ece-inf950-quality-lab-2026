"""Κανόνες τιμολόγησης: κουπόνια, happy hour, χρέωση αποστολής.

Κανόνες της επιχείρησης (απαιτήσεις FR-03, FR-08, FR-09):
- Κουπόνι: αφαιρείται σταθερό ποσό από το υποσύνολο, χωρίς να πέσει κάτω από 0.
- Happy hour: έκπτωση 20% από 17:00 έως πριν τις 19:00.
- Αποστολή: δωρεάν όταν το ποσό μετά από εκπτώσεις είναι τουλάχιστον 15,00 €,
  αλλιώς 2,00 €.
- Όλα τα ποσά στρογγυλοποιούνται στο λεπτό του ευρώ.
"""

from __future__ import annotations

from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

FREE_DELIVERY_THRESHOLD = Decimal("15.00")
DELIVERY_FEE = Decimal("2.00")
HAPPY_HOUR_RATE = Decimal("0.20")
CENT = Decimal("0.01")


def to_cents(amount: Decimal) -> Decimal:
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def apply_coupon(subtotal: Decimal, coupon) -> Decimal:
    coupon = Decimal(str(coupon))
    if coupon < 0:
        raise ValueError("Το κουπόνι δεν μπορεί να είναι αρνητικό")
    return max(subtotal - coupon, Decimal("0.00"))


def happy_hour_discount(amount: Decimal, now: datetime) -> Decimal:
    if 17 <= now.hour <= 19:
        return amount * HAPPY_HOUR_RATE
    return Decimal("0.00")


def delivery_fee(amount_after_discounts: Decimal) -> Decimal:
    if amount_after_discounts > FREE_DELIVERY_THRESHOLD:
        return Decimal("0.00")
    return DELIVERY_FEE


def total(cart, coupon=0, now: datetime | None = None) -> Decimal:
    """Τελικό ποσό: υποσύνολο − κουπόνι − happy hour + αποστολή."""
    if now is None:
        now = datetime.now()
    amount = apply_coupon(cart.subtotal(), coupon)
    amount = amount - happy_hour_discount(amount, now)
    return to_cents(amount + delivery_fee(amount))
