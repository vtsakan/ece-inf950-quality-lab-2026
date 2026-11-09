"""Εβδομάδα 7 · Λυμένο παράδειγμα: white-box tests για το foodorder (cart.py).

Τα tests καλύπτουν τα βασικά μονοπάτια των Cart.add και Cart.set_qty που δεν
εκτελούν τα starter tests και τα tests της Εβδομάδας 6. Τα αναμενόμενα
αποτελέσματα προέρχονται από τις απαιτήσεις του labs/week02/SOLVED.md.
Ο γράφος, η V(G) και τα μονοπάτια βρίσκονται στο labs/week07/SOLVED.md.

Εκτέλεση, από τη ρίζα του αποθετηρίου του μαθήματος, με ενεργό venv:

    cp labs/week06/test_blackbox_w06.py labs/week07/test_whitebox_w07.py foodorder/tests/
    cd foodorder && python -m pytest --cov=foodorder --cov-report=term-missing
"""

from decimal import Decimal as D

import pytest

# ---------------------------------------------------------------------------
# Cart.add: V(G) = 4. Βασική γραμμή A1 (νέο προϊόν) καλύπτεται ήδη.
# ---------------------------------------------------------------------------


@pytest.mark.req("FR-05")
def test_add_negative_price_rejected(cart):
    """TC-WB-01 · A3: qty > 0, τιμή < 0 → απόρριψη, το καλάθι μένει κενό."""
    with pytest.raises(ValueError):
        cart.add("pizza", "-0.01", 1)
    assert cart.is_empty()


@pytest.mark.req("FR-01")
def test_add_existing_product_increases_quantity(cart):
    """TC-WB-02 · A4: το προϊόν υπάρχει ήδη → αυξάνεται η ποσότητα, όχι νέα γραμμή."""
    cart.add("pizza", "9.50", 1)
    cart.add("pizza", "9.50", 2)
    assert len(cart.items()) == 1
    assert cart.subtotal() == D("28.50")


@pytest.mark.req("FR-05")
def test_add_price_zero_accepted(cart):
    """TC-WB-03 · όριο της συνθήκης price < 0: η τιμή 0 είναι έγκυρη."""
    cart.add("νερό", "0.00", 1)
    assert cart.subtotal() == D("0.00") and not cart.is_empty()


# ---------------------------------------------------------------------------
# Cart.set_qty: V(G) = 4. Τα S1 (νέα ποσότητα) και S4 (ποσότητα 0) καλύπτονται
# από τα starter tests.
# ---------------------------------------------------------------------------


def test_set_qty_unknown_product(cart):
    """TC-WB-04 · S2: προϊόν που δεν υπάρχει.

    Καμία απαίτηση δεν ορίζει τη συμπεριφορά. Το test καταγράφει την τρέχουσα
    (KeyError) και η ερώτηση στάλθηκε στην επιχείρηση (SOLVED, Ενότητα 8).
    """
    cart.add("pizza", "9.50", 1)
    with pytest.raises(KeyError):
        cart.set_qty("souvlaki", 2)
    assert cart.subtotal() == D("9.50")


@pytest.mark.req("FR-05")
def test_set_qty_negative_rejected(cart):
    """TC-WB-05 · S3: αρνητική ποσότητα → απόρριψη, η ποσότητα μένει ίδια."""
    cart.add("pizza", "9.50", 2)
    with pytest.raises(ValueError):
        cart.set_qty("pizza", -1)
    assert cart.subtotal() == D("19.00")


@pytest.mark.req("FR-01")
def test_set_qty_to_one(cart):
    """TC-WB-06 · όριο της συνθήκης qty == 0: η ποσότητα 1 κρατά το προϊόν."""
    cart.add("pizza", "9.50", 3)
    cart.set_qty("pizza", 1)
    assert cart.subtotal() == D("9.50") and len(cart.items()) == 1


# ---------------------------------------------------------------------------
# Cart.remove: V(G) = 1, χωρίς απαίτηση.
# ---------------------------------------------------------------------------


def test_remove_product(cart):
    """TC-WB-07 · η μόνη εντολή του remove. Χωρίς απαίτηση (SOLVED, Ενότητα 8)."""
    cart.add("pizza", "9.50", 1)
    cart.add("νερό", "1.00", 1)
    cart.remove("pizza")
    assert cart.subtotal() == D("1.00")


@pytest.mark.req("FR-01")
def test_subtotal_of_empty_cart(cart):
    """TC-WB-08 · βρόχος του subtotal με 0 επαναλήψεις: κενό καλάθι → 0,00 €."""
    assert cart.subtotal() == D("0.00")
