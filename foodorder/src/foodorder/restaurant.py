"""Εστιατόριο και ωράριο λειτουργίας."""

from __future__ import annotations

from datetime import datetime, time


class Restaurant:
    def __init__(self, name: str, opens: time = time(11, 0), closes: time = time(23, 30)) -> None:
        self.name = name
        self.opens = opens
        self.closes = closes

    def is_open(self) -> bool:
        """Επιστρέφει True αν το εστιατόριο δέχεται παραγγελίες τώρα."""
        now = datetime.now().time()
        return self.opens <= now < self.closes
