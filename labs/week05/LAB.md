# Εβδομάδα 5 · Εργαστηριακό σκέλος

Σύνδεση με τη διάλεξη: inspection κατά IEEE 1028, code review σε pull request, ruff, mypy, bandit, Semgrep, ταξινόμηση ευρημάτων.
Ερωτήματα εργασίας: `assignment/week05.md`.

## Προετοιμασία (πριν το εργαστήριο)

Με ενεργό το venv στη ρίζα του αποθετηρίου του μαθήματος (βλ. «Εικονικό περιβάλλον Python (venv)» στο κεντρικό `README.md`):

```bash
git pull
source .venv/bin/activate                 # Windows: .venv\Scripts\Activate.ps1
pip install bandit mypy pip-audit
ruff --version && mypy --version && bandit --version | head -1
```

Το Semgrep είναι προαιρετικό (`pip install semgrep`). Είναι μεγάλο πακέτο, και η πρώτη εκτέλεση αργεί.

## Τα 45 λεπτά

**0–15'. Εργαλεία και ταξινόμηση στο foodorder.** Σε ένα αντίγραφο του foodorder σε δικό σας branch, εφαρμόστε το PR #12 και τρέξτε τα εργαλεία:

```bash
git switch -c pr-12-practice
(cd foodorder && ruff check --line-length 100 --select E,F,B,BLE,S,DTZ,PLR src --statistics)   # πριν το patch
git apply labs/week05/PR-12-foodorder.patch
cd foodorder
ruff check --line-length 100 --select E,F,B,BLE,S,DTZ,PLR src
mypy src
bandit -q -r src
semgrep --metrics=off --config ../labs/week05/rules/pii-log.yaml src   # προαιρετικό
cd .. && git restore . && git switch main && git branch -D pr-12-practice
```

Ποια ευρήματα προσθέτει το PR σε σχέση με την πρώτη εκτέλεση, πριν το patch; Ταξινομήστε τα σε true και false positives και συγκρίνετε με την Ενότητα 4 του `SOLVED.md`.

**15–25'. Λυμένο review.** Διαβάστε τις Ενότητες 3, 5 και 7 του `SOLVED.md`. Πόσες από τις ανωμαλίες είχατε βρει στη διάλεξη; Ποιες βρήκαν μόνο άνθρωποι;

**25–40'. Το PR-01 στο αποθετήριο της ομάδας σας (Ε5.2).** Πρώτα βεβαιωθείτε ότι το `.gitignore` της ομάδας αγνοεί τα αρχεία που παράγουν τα εργαλεία. Αλλιώς μπαίνουν αρχεία `.pyc` μέσα στο PR:

```bash
cat .gitignore      # πρέπει να περιέχει τις παρακάτω γραμμές· όσες λείπουν, προσθέστε τις
printf '.venv/\n__pycache__/\n.pytest_cache/\n.mypy_cache/\n.ruff_cache/\n*.egg-info/\n' >> .gitignore
git add .gitignore && git commit -m "Αγνοούμενα αρχεία εργαλείων"
```

Μετά, με ενεργό το venv της ομάδας:

```bash
git switch main && git pull
git switch -c pr-01
git apply --check <αποθετήριο μαθήματος>/pull_requests/PR-01/PR-01.patch
git apply --index <αποθετήριο μαθήματος>/pull_requests/PR-01/PR-01.patch
git commit -m "PR-01 της ομάδας ανάπτυξης"
git show --stat HEAD          # πρέπει να δείχνει 5 αρχεία, 100 προσθήκες, 6 διαγραφές
cd studyroom && python -m pytest && cd ..
git push -u origin pr-01
```

Το `--index` περνά τις αλλαγές απευθείας στο commit, οπότε τίποτα από όσα δημιουργεί το pytest δεν μπαίνει μέσα.

Στο GitHub πατήστε «Compare & pull request» (pr-01 → main) και αντιγράψτε την περιγραφή από το `PR-01.md`. **Μην** κάνετε merge.

**40–45'. Οργάνωση της inspection (Ε5.4).** Μοιράστε ρόλους και οπτικές ανάγνωσης και ορίστε ώρα συνάντησης. Η προετοιμασία γίνεται ατομικά, πριν τη συνάντηση.

## Αν το `git apply` αποτύχει

- **«patch does not apply».** Ο φάκελος `studyroom/` σας έχει αλλαγές κώδικα από την παράδοση 0.1. Οι ρυθμίσεις στο `pyproject.toml` δεν πειράζουν. Επαναφέρετε τον κώδικα στο commit «StudyRoom 0.1 όπως παραδόθηκε» και ξαναδοκιμάστε.
- **Windows και αλλαγές γραμμής.** Δοκιμάστε `git apply --ignore-whitespace`, ή ρυθμίστε `git config core.autocrlf input` πριν από το clone.
- **Ο φάκελος δεν λέγεται `studyroom/`.** Το patch περιμένει τον κώδικα στο `studyroom/` στη ρίζα του αποθετηρίου. Χρησιμοποιήστε `git apply -p2 --directory=<φάκελος>` ή μετονομάστε τον φάκελο.

## Χρήσιμες επιλογές

- `ruff check --statistics src`: πλήθος ευρημάτων ανά κανόνα.
- `ruff check --select ARG src`: αχρησιμοποίητα ορίσματα.
- `mypy --strict src` ή `mypy --check-untyped-defs src`: ελέγχει και συναρτήσεις χωρίς type hints.
- `mypy --enable-error-code possibly-undefined src`: μεταβλητές που ίσως δεν έχουν οριστεί (βλ. A-04 του SOLVED).
- `bandit -c pyproject.toml -r src`: το bandit διαβάζει τις ρυθμίσεις του `[tool.bandit]` μόνο με `-c`.
- Στο `pyproject.toml`, `[tool.ruff.lint.per-file-ignores]` με `"tests/*" = ["S101"]`: τα assert στα tests δεν είναι εύρημα.
- `pip-audit`: ευπάθειες στα πακέτα του venv.
- `bandit -r src -f csv -o bandit.csv`: έξοδος για τη λίστα ανωμαλιών.
- `git diff main...pr-01 --stat`: μέγεθος της αλλαγής, για τις μετρήσεις της Ενότητας 7.

## Συχνά λάθη

- Η έξοδος των εργαλείων αντιγραμμένη ως «λίστα ανωμαλιών», χωρίς ταξινόμηση και χωρίς ανωμαλίες από ανθρώπους.
- Ευρήματα του main μετρημένα ως ευρήματα του PR.
- Σχόλια στο PR χωρίς σοβαρότητα, ή χωρίς την απαίτηση που παραβιάζεται.
- Approve με κρίσιμες ανωμαλίες ανοιχτές.
- Merge του PR ή διόρθωση του κώδικά του.
- Αγνόηση των απαντήσεων της βιβλιοθήκης στο forum (Φ1–Φ9), που είναι πλέον προδιαγραφές.
