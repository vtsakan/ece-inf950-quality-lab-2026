# Εβδομάδα 4 · Εργαστηριακό σκέλος

Σύνδεση με τη διάλεξη: ISO/IEC/IEEE 15939, LOC, Halstead, McCabe, γνωστική πολυπλοκότητα, maintainability index, code smells, τεχνικό χρέος.
Ερωτήματα εργασίας: `assignment/week04.md`.

## Προετοιμασία (πριν το εργαστήριο)

Όλα τα εργαλεία εγκαθίστανται σε εικονικό περιβάλλον (venv), στη ρίζα του αποθετηρίου του μαθήματος. Οδηγίες και συνηθισμένα προβλήματα (Ubuntu, Windows) υπάρχουν στο κεντρικό `README.md`, στην ενότητα «Εικονικό περιβάλλον Python (venv)».

```bash
cd ece-inf950-quality-lab-2026            # ρίζα του αποθετηρίου του μαθήματος
git pull
python3 -m venv .venv                     # μόνο την πρώτη φορά
source .venv/bin/activate                 # σε κάθε νέο τερματικό· Windows: .venv\Scripts\Activate.ps1
pip install -e "./foodorder[dev]" -e "./studyroom[dev]" complexipy
radon --version && ruff --version && complexipy --version
```

Η γραμμή εντολών πρέπει να ξεκινά με `(.venv)`. Αν όχι, τα εργαλεία δεν θα βρεθούν.

## Τα 45 λεπτά

**0–5'. Λυμένο παράδειγμα.** Ανοίγουμε το `SOLVED.md`. Είναι η αναφορά μετρήσεων του `foodorder`, γραμμένη με το υπόδειγμα w04.

**5–20'. Μέτρηση του foodorder.** Από τον φάκελο `foodorder/`, με ενεργό το venv:

```bash
radon raw -s src
radon cc -s -a src
radon mi -s src
radon hal -f src/foodorder/pricing.py
complexipy src
ruff check --line-length 100 --select E,F,B,C90,PLR,SIM,DTZ src
pytest --cov=foodorder --cov-branch
```

Συγκρίνετε τους αριθμούς σας με την Ενότητα 4 του `SOLVED.md`. Αν διαφέρουν, γράψτε γιατί: έκδοση εργαλείου, ρυθμίσεις, λειτουργικό. Αυτή είναι η πρώτη άσκηση αναπαραγωγιμότητας.

**20–30'. Με το χέρι.** Υπολογίστε Halstead και V(G) για την `pricing.delivery_fee` με τους κανόνες του `SOLVED.md`. Ελέγξτε το V(G) με το `radon cc` και τον Halstead με το `radon hal -f`, και εξηγήστε τις διαφορές.

**30–40'. Παραλαβή του StudyRoom.** Αντιγράψτε τον φάκελο `studyroom/` στο αποθετήριο της ομάδας σας και κάντε commit πριν αλλάξετε οτιδήποτε (Ε4.1):

```bash
cp -r <αποθετήριο μαθήματος>/studyroom <αποθετήριο ομάδας>/
cd <αποθετήριο ομάδας>
git add studyroom && git commit -m "StudyRoom 0.1 όπως παραδόθηκε"
python3 -m venv .venv && source .venv/bin/activate     # venv και στο αποθετήριο της ομάδας
pip install -e "./studyroom[dev]" complexipy
cd studyroom && python -m pytest
```

Βεβαιωθείτε ότι το `.gitignore` της ομάδας σας περιέχει τις γραμμές `.venv/`, `__pycache__/` και `*.egg-info/`.

Τρέξτε τις ίδιες εντολές με το foodorder στο `studyroom/src`. Σημειώστε τα τρία πρώτα σημεία που σας κάνουν εντύπωση.

**40–45'. Ισχυρισμοί.** Διαβάστε το `studyroom/RELEASE_NOTES.md`. Για καθέναν από τους Κ1–Κ6 γράψτε ποια εντολή ή ποιο μέρος του κώδικα θα τον επιβεβαίωνε ή θα τον διέψευδε. Η τεκμηρίωση ολοκληρώνεται στο σπίτι (Ε4.9).

## Χρήσιμες επιλογές

- `radon cc -s -n C src`: μόνο συναρτήσεις με βαθμίδα C ή χειρότερη.
- `radon cc -s -j src > cc.json`: έξοδος JSON για ταξινόμηση ή γράφημα.
- `radon mi -s -m src`: MI χωρίς να μετρώνται τα docstrings ως σχόλια.
- `ruff check --statistics src`: πλήθος ευρημάτων ανά κανόνα.
- `pylint --disable=all --enable=R0801 --min-similarity-lines=4 src/studyroom`: διπλότυπα.
- `npx jscpd --min-lines 3 --min-tokens 30 src`: διπλότυπα, χρειάζεται Node.js.

## Συχνά λάθη

- Έξοδος εργαλείου στην αναφορά χωρίς εκδόσεις, ρυθμίσεις και ερμηνεία.
- Μέσος όρος πολυπλοκότητας χωρίς κατανομή και χωρίς τις χειρότερες περιπτώσεις.
- Σύγκριση Halstead με το χέρι και με το radon σαν να ήταν το ίδιο μέτρο.
- «Ο κώδικας είναι καλός γιατί όλα είναι A.»
- Διόρθωση του κώδικα του StudyRoom. Αυτή την εβδομάδα μόνο μετράμε.
- Smells χωρίς αρχείο και γραμμή.
