"""Καλάθι αγορών."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Item:
    name: str
    unit_price: Decimal
    qty: int

    def line_total(self) -> Decimal:
        return self.unit_price * self.qty


class Cart:
    """Καλάθι με προϊόντα, ποσότητες και υποσύνολο σε ευρώ."""

    def __init__(self) -> None:
        self._items: dict[str, Item] = {}

    def add(self, name: str, unit_price, qty: int = 1) -> None:
        """Προσθέτει προϊόν ή αυξάνει την ποσότητα αν υπάρχει ήδη."""
        if qty <= 0:
            raise ValueError("Η ποσότητα πρέπει να είναι θετική")
        price = Decimal(str(unit_price))
        if price < 0:
            raise ValueError("Η τιμή δεν μπορεί να είναι αρνητική")
        if name in self._items:
            self._items[name].qty += qty
        else:
            self._items[name] = Item(name, price, qty)

    def set_qty(self, name: str, qty: int) -> None:
        """Ορίζει νέα ποσότητα. Ποσότητα 0 αφαιρεί το προϊόν."""
        if name not in self._items:
            raise KeyError(name)
        if qty < 0:
            raise ValueError("Η ποσότητα δεν μπορεί να είναι αρνητική")
        if qty == 0:
            del self._items[name]
        else:
            self._items[name].qty = qty

    def remove(self, name: str) -> None:
        del self._items[name]

    def clear(self) -> None:
        self._items.clear()

    def items(self) -> list[Item]:
        return list(self._items.values())

    def is_empty(self) -> bool:
        return not self._items

    def subtotal(self) -> Decimal:
        return sum(
            (item.line_total() for item in self._items.values()),
            Decimal("0.00"),
        )
