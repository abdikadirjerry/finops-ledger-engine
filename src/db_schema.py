import sqlite3
from pathlib import Path


def get_connection(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database(db_path: str | Path) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cost_budgets (
                cost_center TEXT PRIMARY KEY,
                monthly_cap_cents INTEGER NOT NULL CHECK (monthly_cap_cents >= 0)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ledger_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recorded_date TEXT NOT NULL,
                vendor_service TEXT NOT NULL,
                cost_center TEXT NOT NULL,
                environment TEXT NOT NULL,
                entry_type TEXT NOT NULL,
                amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
                memo TEXT NOT NULL,
                FOREIGN KEY (cost_center) REFERENCES cost_budgets(cost_center)
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ledger_center_date ON ledger_entries(cost_center, recorded_date DESC);"
        )
