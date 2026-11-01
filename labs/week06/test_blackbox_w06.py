"""Εβδομάδα 6 · Λυμένο παράδειγμα: black-box tests για το foodorder.

Τα αναμενόμενα αποτελέσματα προέρχονται από τις απαιτήσεις του
labs/week02/SOLVED.md, όχι από τον κώδικα. Κάθε test έχει ID (TC-BB-xx)
και το marker req με την απαίτηση. Η αντιστοίχιση με τα μοντέλα και τα
στοιχεία κάλυψης βρίσκεται στο labs/week06/SOLVED.md.

Εκτέλεση, από τη ρίζα του αποθετηρίου του μαθήματος, με ενεργό venv:

    cp labs/week06/test_blackbox_w06.py foodorder/tests/
    cd foodorder && python -m pytest tests/test_blackbox_w06.py -v
"""

from datetime import datetime
from decimal import Decimal as D

import pytest

from foodorder import Cart
from foodorder.checkout import (
    CheckoutService,
    EmptyCartError,
    PaymentDeclinedError,
    RestaurantClosedError,
)
from foodorder.orders import InvalidTransitionError, Order, Status
from foodorder.payments import SandboxGateway
from foodorder.pricing import total

MON = (2026, 11, 2)                 # Δευτέρα· μόνο η ώρα αλλάζει


def at(h, m=0, s=0):
    return datetime(*MON, h, m, s)


def cart_of(amount):
    c = Cart()
    c.add("προϊόν", amount, 1)
    return c


# ---------------------------------------------------------------------------
# 1. FR-08 · happy hour, διαμέριση και οριακές τιμές 3 τιμών (μοντέλο 2.1, 2.2)
#    Υποσύνολο 20,00 €: μέσα στο happy hour 16,00 €, έξω 20,00 €.
#    Και στις δύο περιπτώσεις η αποστολή είναι δωρεάν (≥ 15,00 €), ώστε να
#    ελέγχεται μόνο η FR-08.
# ---------------------------------------------------------------------------
HAPPY = [
    ("TC-BB-01", at(12, 0), "20.00"),        # EC1 πριν το happy hour
    ("TC-BB-02", at(16, 59, 59), "20.00"),   # B1−
    ("TC-BB-03", at(17, 0, 0), "16.00"),     # B1
    ("TC-BB-04", at(17, 0, 1), "16.00"),     # B1+
    ("TC-BB-05", at(18, 0), "16.00"),        # EC2 μέσα στο happy hour
    ("TC-BB-06", at(18, 59, 59), "16.00"),   # B2−
    ("TC-BB-07", at(19, 0, 0), "20.00"),     # B2
    ("TC-BB-08", at(19, 0, 1), "20.00"),     # B2+
    ("TC-BB-09", at(19, 59, 59), "20.00"),   # εικασία σφάλματος: σύγκριση μόνο της ώρας
    ("TC-BB-10", at(21, 0), "20.00"),        # EC3 μετά το happy hour
]


@pytest.mark.req("FR-08")
@pytest.mark.parametrize("now, expected", [h[1:] for h in HAPPY], ids=[h[0] for h in HAPPY])
def test_happy_hour(now, expected):
    assert total(cart_of("20.00"), coupon=0, now=now) == D(expected)


# ---------------------------------------------------------------------------
# 2. FR-03 · όριο δωρεάν αποστολής, στην είσοδο και στην έξοδο (2.2)
# ---------------------------------------------------------------------------
DELIVERY = [
    ("TC-BB-11", "14.99", at(12), "16.99"),  # B3−
    ("TC-BB-12", "15.00", at(12), "15.00"),  # B3
    ("TC-BB-13", "15.01", at(12), "15.01"),  # B3+
    ("TC-BB-14", "18.75", at(18), "15.00"),  # όριο εξόδου: 18,75 × 0,8 = 15,00 μετά το happy hour
]


@pytest.mark.req("FR-03")
@pytest.mark.parametrize("subtotal, now, expected", [d[1:] for d in DELIVERY], ids=[d[0] for d in DELIVERY])
def test_delivery_threshold(subtotal, now, expected):
    assert total(cart_of(subtotal), coupon=0, now=now) == D(expected)


# ---------------------------------------------------------------------------
# 3. FR-06 · κουπόνι (2.1, 2.2). Υποσύνολο 10,00 €, ώρα 12:00.
# ---------------------------------------------------------------------------
COUPON = [
    ("TC-BB-15", "0", "12.00"),       # B4: κουπόνι 0
    ("TC-BB-16", "4.00", "8.00"),     # EC5 κουπόνι μικρότερο από το υποσύνολο
    ("TC-BB-17", "10.00", "2.00"),    # B5: κουπόνι ίσο με το υποσύνολο
    ("TC-BB-18", "10.01", "2.00"),    # B5+: το ποσό δεν γίνεται αρνητικό
]


@pytest.mark.req("FR-06")
@pytest.mark.parametrize("coupon, expected", [c[1:] for c in COUPON], ids=[c[0] for c in COUPON])
def test_coupon(coupon, expected):
    assert total(cart_of("10.00"), coupon=coupon, now=at(12)) == D(expected)


@pytest.mark.req("FR-06")
def test_negative_coupon_rejected():
    """TC-BB-19 · EC6 άκυρη κλάση: κουπόνι −0,01."""
    with pytest.raises(ValueError):
        total(cart_of("10.00"), coupon="-0.01", now=at(12))


# ---------------------------------------------------------------------------
# 4. FR-02, FR-07, FR-10 · πίνακας αποφάσεων ολοκλήρωσης παραγγελίας (2.3)
#    Το εστιατόριο αντικαθίσταται στο όριο της υπηρεσίας: το CheckoutService
#    δέχεται οποιοδήποτε αντικείμενο με is_open().
# ---------------------------------------------------------------------------
class Restaurant:
    def __init__(self, open_):
        self.name = "Δοκιμή"
        self._open = open_

    def is_open(self):
        return self._open


@pytest.mark.req("FR-02", "FR-07", "FR-10")
def test_R1_order_created():
    """TC-BB-20 · R1: μη κενό, ανοιχτό, εγκρίνεται → παραγγελία, άδειο καλάθι."""
    cart = cart_of("20.00")
    order = CheckoutService(SandboxGateway(), Restaurant(True)).place_order(cart, "tok", now=at(12))
    assert order.status is Status.SUBMITTED and order.total == D("20.00") and cart.is_empty()


@pytest.mark.req("FR-10")
def test_R2_payment_declined_keeps_cart():
    """TC-BB-21 · R2: απόρριψη πληρωμής → αιτία, καλάθι ως είχε."""
    cart = cart_of("20.00")
    with pytest.raises(PaymentDeclinedError) as e:
        CheckoutService(SandboxGateway(), Restaurant(True)).place_order(cart, "declined-1", now=at(12))
    assert e.value.reason == "card_declined" and cart.subtotal() == D("20.00")


@pytest.mark.req("FR-07")
def test_R3_restaurant_closed():
    """TC-BB-22 · R3: μη κενό, κλειστό → «εκτός ωραρίου», καμία χρέωση."""
    gw = SandboxGateway()
    with pytest.raises(RestaurantClosedError):
        CheckoutService(gw, Restaurant(False)).place_order(cart_of("20.00"), "tok", now=at(12))
    assert gw.charges == {}


@pytest.mark.req("FR-02")
def test_R4_empty_cart():
    """TC-BB-23 · R4: κενό καλάθι → «κενό καλάθι». Για τις παύλες: ανοιχτό, κάρτα εγκρίνεται."""
    with pytest.raises(EmptyCartError):
        CheckoutService(SandboxGateway(), Restaurant(True)).place_order(Cart(), "tok", now=at(12))


# ---------------------------------------------------------------------------
# 5. FR-11, FR-13 · μεταβάσεις κατάστασης παραγγελίας (2.4)
# ---------------------------------------------------------------------------
PATH = {  # η συντομότερη έγκυρη ακολουθία προς κάθε κατάσταση
    Status.SUBMITTED: [],
    Status.ACCEPTED: ["accept"],
    Status.PREPARING: ["accept", "start_preparing"],
    Status.DISPATCHED: ["accept", "start_preparing", "dispatch"],
    Status.DELIVERED: ["accept", "start_preparing", "dispatch", "deliver"],
    Status.CANCELLED: ["cancel"],
}


def make_order(state):
    gw = SandboxGateway()
    ref = gw.authorize(D("20.00"), "tok").ref
    order = Order(total=D("20.00"), payment_ref=ref, lines=[])
    for event in PATH[state]:
        fire(order, event, gw)
    return order, gw


def fire(order, event, gw):
    if event == "cancel":
        return order.cancel_by_customer(gw)
    return getattr(order, event)()


VALID = [
    ("TC-BB-24", Status.SUBMITTED, "accept", Status.ACCEPTED),
    ("TC-BB-25", Status.ACCEPTED, "start_preparing", Status.PREPARING),
    ("TC-BB-26", Status.PREPARING, "dispatch", Status.DISPATCHED),
    ("TC-BB-27", Status.DISPATCHED, "deliver", Status.DELIVERED),
    ("TC-BB-28", Status.SUBMITTED, "cancel", Status.CANCELLED),
]


@pytest.mark.req("FR-11", "FR-13")
@pytest.mark.parametrize("state, event, target", [v[1:] for v in VALID], ids=[v[0] for v in VALID])
def test_valid_transition(state, event, target):
    order, gw = make_order(state)
    fire(order, event, gw)
    assert order.status is target
    if event == "cancel":
        assert gw.refunds[order.payment_ref] == order.total      # FR-11: ολόκληρο το ποσό


EVENTS = ["accept", "start_preparing", "dispatch", "deliver", "cancel"]
VALID_PAIRS = {(v[1], v[2]) for v in VALID}
INVALID = [(s, e) for s in Status for e in EVENTS if (s, e) not in VALID_PAIRS]
INVALID_IDS = [f"TC-BB-{29 + i:02d}-{s.name}-{e}" for i, (s, e) in enumerate(INVALID)]


@pytest.mark.req("FR-11", "FR-13")
@pytest.mark.parametrize("state, event", INVALID, ids=INVALID_IDS)
def test_invalid_transition(state, event):
    order, gw = make_order(state)
    refunds_before = dict(gw.refunds)
    with pytest.raises(InvalidTransitionError):
        fire(order, event, gw)
    assert order.status is state            # η κατάσταση δεν άλλαξε
    assert gw.refunds == refunds_before     # καμία επιστροφή χρημάτων
