# Εβδομάδα 7 · Εργαστηριακό σκέλος

Σύνδεση με τη διάλεξη: γράφος ροής ελέγχου, κυκλωματική πολυπλοκότητα, βασικά μονοπάτια, κάλυψη εντολών και διακλαδώσεων, μέτρηση με coverage.py και pytest-cov.
Ερωτήματα εργασίας: `assignment/week07.md`.

## Προετοιμασία (πριν το εργαστήριο)

Με ενεργό το venv στη ρίζα του αποθετηρίου του μαθήματος:

```bash
git pull
source .venv/bin/activate                 # Windows: .venv\Scripts\Activate.ps1
python -c "import pytest_cov; print('pytest-cov εντάξει')" || pip install pytest-cov
```

Για τους γράφους σε Mermaid αρκεί το GitHub ή το https://mermaid.live. Για εικόνα από τη γραμμή εντολών: `npx @mermaid-js/mermaid-cli -i graph.mmd -o graph.png`.

## Τα 45 λεπτά

**0–10'. Η κάλυψη που υπάρχει.** Οι απαιτήσεις του foodorder (FR-01 έως FR-13) είναι στο `labs/week02/SOLVED.md`. Τα `pyproject.toml` έχουν ήδη `branch = true`, οπότε μετριούνται και διακλαδώσεις.

```bash
cp labs/week06/test_blackbox_w06.py foodorder/tests/
cd foodorder
python -m pytest tests/test_cart_starter.py --cov=foodorder --cov-report=term-missing    # 56%
python -m pytest --cov=foodorder --cov-report=term-missing                              # 92%
```

Με τα tests της Εβδομάδας 6 η κάλυψη ανεβαίνει στο 92% και 6 tests αποτυγχάνουν: είναι τα ελαττώματα που βρήκε το λυμένο της Εβδομάδας 6. Για κάθε γραμμή που μένει στο Missing, αποφασίστε σε ποια κατηγορία ανήκει: κανόνας χωρίς test, αδύνατο μονοπάτι, νεκρός κώδικας, πρόβλημα ελεγξιμότητας. Συγκρίνετε με την Ενότητα 8 του `SOLVED.md`.

**10–25'. Γράφος και βασικά μονοπάτια για το `Cart.set_qty`.** Χωρίς να κοιτάξετε το `SOLVED.md`:

1. Αριθμήστε τους κόμβους του `Cart.set_qty` (γραμμές 37–46 του `cart.py`) και γράψτε τον γράφο σε Mermaid.
2. Υπολογίστε τη V(G) με δύο τρόπους και συγκρίνετε με το `radon cc -s src/foodorder/cart.py`.
3. Βρείτε τα βασικά μονοπάτια με τη μέθοδο της βασικής γραμμής. Ποια εκτελούν ήδη τα starter tests;
4. Για κάθε μονοπάτι γράψτε το αναμενόμενο αποτέλεσμα **από απαίτηση**. Για ποιο μονοπάτι δεν υπάρχει απαίτηση;

Επαναλάβετε για το `Cart.add` (γραμμές 25–35), αν μείνει χρόνος.

**25–35'. Tests ώσπου το `cart.py` να φτάσει 100%.** Γράψτε στο `foodorder/tests/test_whitebox_w07.py` ένα test για κάθε μονοπάτι που δεν εκτελείται ακόμη, με marker `req` όπου υπάρχει απαίτηση. Μετά:

```bash
python -m pytest --cov=foodorder --cov-report=term-missing
python -m pytest --cov=foodorder --cov-report=html && xdg-open htmlcov/index.html
cd ..
```

Πρέπει να δείτε `cart.py` στο 100% και σύνολο 96%. Συγκρίνετε τα tests σας με το `labs/week07/test_whitebox_w07.py`. Τα αντίγραφα στο `foodorder/tests/` αγνοούνται από το `.gitignore`.

**35–45'. Ξεκίνημα στο StudyRoom (Ε7.1, Ε7.2).** Στο αποθετήριο της ομάδας σας:

```bash
git switch main && git pull
mkdir -p studyroom/tests/whitebox
cd studyroom
python -m pytest --cov=studyroom --cov-report=term-missing     # κάλυψη «πριν», με τα tests της w06
radon cc -s src/studyroom/penalties.py src/studyroom/reports.py
cd ..
```

Μοιράστε τις πέντε μονάδες της εργασίας στα μέλη της ομάδας για τους γράφους.

## Χρήσιμες επιλογές

- `--cov-report=term-missing:skip-covered`: μόνο τα αρχεία που δεν είναι στο 100%.
- `--cov=studyroom.penalties`: μέτρηση μόνο ενός module.
- `--cov-context=test` και στο `pyproject.toml` `[tool.coverage.html] show_contexts = true`: το HTML δείχνει ποιο test εκτέλεσε κάθε γραμμή.
- `coverage report -m --include="*/penalties.py"`: η αναφορά για ένα αρχείο, μετά από μια εκτέλεση.
- `pytest.mark.xfail(strict=True, reason="INC-01")`: test που αναμένεται να αποτύχει μέχρι να διορθωθεί το ελάττωμα. Το `strict=True` το κάνει αποτυχία όταν αρχίσει να περνά.
- Αν θέλετε το marker `req` και στο StudyRoom, δηλώστε το στο `studyroom/pyproject.toml`: `[tool.pytest.ini_options]` με `markers = ["req(id): απαίτηση ή κανόνας που ελέγχει το test"]`.

## Συχνά λάθη

- Σύνθετη συνθήκη σε έναν κόμβο του γράφου, οπότε η V(G) βγαίνει μικρότερη από τον αριθμό των ατομικών αποφάσεων + 1.
- Αναμενόμενο αποτέλεσμα από τον κώδικα που ελέγχεται.
- Test για «αδύνατο» μονοπάτι που στην πράξη περνά από άλλο μονοπάτι. Ελέγξτε με το HTML ποιες γραμμές εκτέλεσε.
- `# pragma: no cover` χωρίς αιτιολόγηση, ή tests χωρίς assert για να ανέβει το ποσοστό.
- Διόρθωση του κώδικα. Αυτή την εβδομάδα τα ελαττώματα καταγράφονται, δεν διορθώνονται.
