# VerdantLedger — Zero-Dependency Cloud FinOps & Double-Entry Budget Engine (`python-finops-ledger-engine`)

A multi-tab FinOps cost governance, budget variance tracking, and cloud expenditure ledger web application built exclusively with Python's standard library (`http.server`, `sqlite3`, `decimal`, `csv`, `json`).

## Key Modules
- **Exact Integer-Cents Ledger (`src/models.py` & `src/ledger_repo.py`):** Converts dollar inputs using `decimal.Decimal` (`ROUND_HALF_UP`) to prevent floating-point drift across `EXPENSE`, `CREDIT`, and `RESERVATION` entries.
- **SQLite Relational Schema (`src/db_schema.py`):** Enforces foreign keys between `ledger_entries` and `cost_budgets` with indexed date/cost-center lookups.
- **Variance & Environment Analytics (`src/analytics.py`):** Computes real-time cost center utilization percentages, remaining allowances, and `prod` / `staging` / `sandbox` spend shares.
- **RFC-4180 CSV & JSON Audit Exports (`src/exporters.py`):** Streams downloadable CSV statements (`/export/ledger.csv`) and machine-readable audit snapshots (`/api/audit`).

## Running Locally
```bash
python3 app.py
```
Open `http://127.0.0.1:8098` in your browser, or run the full test suite:
```bash
python3 -m unittest discover -s tests -v
```
