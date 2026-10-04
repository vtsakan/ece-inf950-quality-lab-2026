# foodorder

Εκπαιδευτικό σύστημα παραγγελίας φαγητού για το ECE_INF950 Ποιότητα Λογισμικού.

## Εγκατάσταση

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## Τμήματα

`cart.py` καλάθι · `pricing.py` κουπόνια, happy hour, χρέωση αποστολής ·
`restaurant.py` ωράριο · `orders.py` καταστάσεις παραγγελίας ·
`payments.py` διεπαφή πύλης πληρωμών · `checkout.py` ολοκλήρωση παραγγελίας.

Οι απαιτήσεις του συστήματος βρίσκονται στο `labs/week02/SOLVED.md`.
