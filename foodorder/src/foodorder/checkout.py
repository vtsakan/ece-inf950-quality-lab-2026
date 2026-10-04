"""Ολοκλήρωση παραγγελίας (use case «Ολοκλήρωση παραγγελίας»)."""

from __future__ import annotations

from datetime import datetime

from . import pricing
from .orders import Order


class EmptyCartError(Exception):
    pass


class RestaurantClosedError(Exception):
    pass


class PaymentDeclinedError(Exception):
    def __init__(self, reason: str | None) -> None:
        super().__init__(reason)
        self.reason = reason


class CheckoutService:
    def __init__(self, gateway, restaurant) -> None:
        self.gateway = gateway
        self.restaurant = restaurant

    def place_order(self, cart, card_token: str, coupon=0, now: datetime | None = None) -> Order:
        if cart.is_empty():
            raise EmptyCartError()
        if not self.restaurant.is_open():
            raise RestaurantClosedError(self.restaurant.name)

        amount = pricing.total(cart, coupon, now)
        result = self.gateway.authorize(amount, card_token)
        if not result.ok:
            # Το καλάθι διατηρείται ώστε ο χρήστης να δοκιμάσει άλλη κάρτα.
            raise PaymentDeclinedError(result.reason)

        lines = [(i.name, i.qty, i.unit_price) for i in cart.items()]
        order = Order(total=amount, payment_ref=result.ref, lines=lines)
        cart.clear()
        return order
