"""Αρχικά tests που συνοδεύουν το σύστημα.

Δείχνουν μόνο τη δομή. Η κάλυψη είναι σκόπιμα μικρή: τα υπόλοιπα
γράφονται στο εργαστήριο (Εβδομάδες 6–9).
"""

from decimal import Decimal

import pytest


@pytest.mark.req("FR-01")
def test_subtotal_after_quantity_change(cart):
    cart.add("pizza", "9.50")
    cart.set_qty("pizza", 3)
    assert cart.subtotal() == Decimal("28.50")


@pytest.mark.req("FR-02")
def test_setting_quantity_to_zero_removes_item(cart):
    cart.add("souvlaki", "3.50")
    cart.set_qty("souvlaki", 0)
    assert cart.is_empty()


@pytest.mark.req("FR-05")
def test_negative_quantity_is_rejected(cart):
    with pytest.raises(ValueError):
        cart.add("pizza", "9.50", qty=-1)
