from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from src.db_schema import get_connection, initialize_database
from src.models import (
    LedgerEntry,
    VALID_COST_CENTERS,
    VALID_ENTRY_TYPES,
    VALID_ENVIRONMENTS,
)
from src.seeder import seed_if_empty


def parse_dollars_to_cents(raw_amount: str) -> int:
    cleaned = raw_amount.strip().replace("$", "").replace(",", "")
    try:
        dec = Decimal(cleaned)
    except InvalidOperation:
        return 100
    cents = int((dec * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return max(1, cents)


class FinOpsRepository:
    def __init__(self, db_path: str = "data/finops_ledger.db"):
        self.db_path = Path(db_path)
        initialize_database(self.db_path)
        seed_if_empty(self.db_path)

    def add_entry(
        self,
        recorded_date: str,
        vendor_service: str,
        cost_center: str,
        environment: str,
        entry_type: str,
        raw_amount_dollars: str,
        memo: str,
    ) -> int:
        safe_date = recorded_date.strip()[:10] or date.today().isoformat()
        safe_vendor = vendor_service.strip()[:80] or "Cloud Infrastructure"
        safe_center = cost_center if cost_center in VALID_COST_CENTERS else VALID_COST_CENTERS[0]
        safe_env = environment if environment in VALID_ENVIRONMENTS else "prod"
        safe_type = entry_type if entry_type in VALID_ENTRY_TYPES else "EXPENSE"
        cents = parse_dollars_to_cents(raw_amount_dollars)
        safe_memo = memo.strip()[:140] or "Standard cloud allocation"

        with get_connection(self.db_path) as conn:
            cur = conn.execute(
                """
                INSERT INTO ledger_entries
                (recorded_date, vendor_service, cost_center, environment, entry_type, amount_cents, memo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (safe_date, safe_vendor, safe_center, safe_env, safe_type, cents, safe_memo),
            )
            return int(cur.lastrowid)

    def delete_entry(self, entry_id: int) -> None:
        with get_connection(self.db_path) as conn:
            conn.execute("DELETE FROM ledger_entries WHERE id = ?", (entry_id,))

    def update_budget_cap(self, cost_center: str, raw_cap_dollars: str) -> None:
        if cost_center not in VALID_COST_CENTERS:
            return
        cents = parse_dollars_to_cents(raw_cap_dollars)
        with get_connection(self.db_path) as conn:
            conn.execute(
                "UPDATE cost_budgets SET monthly_cap_cents = ? WHERE cost_center = ?",
                (cents, cost_center),
            )

    def list_entries(self, center_filter: str = "ALL", env_filter: str = "ALL") -> list[LedgerEntry]:
        query = "SELECT * FROM ledger_entries WHERE 1=1"
        params: list[str] = []

        if center_filter != "ALL" and center_filter in VALID_COST_CENTERS:
            query += " AND cost_center = ?"
            params.append(center_filter)

        if env_filter != "ALL" and env_filter in VALID_ENVIRONMENTS:
            query += " AND environment = ?"
            params.append(env_filter)

        query += " ORDER BY recorded_date DESC, id DESC"

        with get_connection(self.db_path) as conn:
            rows = conn.execute(query, params).fetchall()
            return [
                LedgerEntry(
                    id=int(r["id"]),
                    recorded_date=str(r["recorded_date"]),
                    vendor_service=str(r["vendor_service"]),
                    cost_center=str(r["cost_center"]),
                    environment=str(r["environment"]),
                    entry_type=str(r["entry_type"]),
                    amount_cents=int(r["amount_cents"]),
                    memo=str(r["memo"]),
                )
                for r in rows
            ]

    def get_budget_caps(self) -> dict[str, int]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute("SELECT cost_center, monthly_cap_cents FROM cost_budgets").fetchall()
            return {str(r["cost_center"]): int(r["monthly_cap_cents"]) for r in rows}
