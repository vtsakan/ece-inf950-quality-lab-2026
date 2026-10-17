# StudyRoom 0.1

Σύστημα κρατήσεων αιθουσών μελέτης της βιβλιοθήκης. Έκδοση 0.1, παράδοση της ομάδας ανάπτυξης.

## Εγκατάσταση

Με εικονικό περιβάλλον (venv), από τη ρίζα του αποθετηρίου που περιέχει τον φάκελο `studyroom/`:

```bash
python3 -m venv .venv                 # μόνο την πρώτη φορά
source .venv/bin/activate             # σε κάθε νέο τερματικό· Windows: .venv\Scripts\Activate.ps1
pip install -e "./studyroom[dev]"
cd studyroom && python -m pytest
```

Χωρίς ενεργό venv, σε Ubuntu το `pip install` αποτυγχάνει (`externally-managed-environment`) και το `python3 -m pytest` απαντά `No module named pytest`.

Χωρίς τη μεταβλητή περιβάλλοντος `STUDYROOM_SMTP` δεν στέλνονται email· τα μηνύματα κρατιούνται στη λίστα `notify.SENT`.

## Τμήματα

`models.py` οντότητες · `rules.py` κανόνες της βιβλιοθήκης · `store.py` αποθήκευση στη μνήμη ·
`booking.py` έλεγχος και δημιουργία κράτησης, ακύρωση, check-in, χαμένες κρατήσεις ·
`penalties.py` αποκλεισμός · `notify.py` email · `reports.py` αναφορές πληρότητας ·
`admin.py` είσοδος αιτημάτων από τη διεπαφή · `auth.py` σύνδεση (προσωρινή) · `seed.py` αρχικά δεδομένα.

Το ημερολόγιο εξεταστικών φορτώνεται από το `data/exams_2026_27.csv`.

Το σημείωμα παράδοσης της ομάδας ανάπτυξης βρίσκεται στο `RELEASE_NOTES.md`.
