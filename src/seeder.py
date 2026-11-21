from pathlib import Path
from src.db_schema import get_connection

DEFAULT_BUDGETS = [
    ("Compute-K8s", 450000),      # $4,500.00
    ("Database-RDS", 320000),     # $3,200.00
    ("Object-Storage", 120000),   # $1,200.00
    ("Network-CDN", 150000),      # $1,500.00
    ("Observability", 95000),     # $950.00
]

DEFAULT_ENTRIES = [
    ("2026-11-02", "AWS EKS Worker Nodes", "Compute-K8s", "prod", "EXPENSE", 184500, "eu-central-1 c6i.2xlarge cluster"),
    ("2026-11-05", "PostgreSQL Multi-AZ", "Database-RDS", "prod", "EXPENSE", 248000, "Primary ledger & auth DBs"),
    ("2026-11-08", "S3 Glacier Archive", "Object-Storage", "prod", "EXPENSE", 41250, "Compliance log retention buckets"),
    ("2026-11-11", "CloudFront Edge Egress", "Network-CDN", "prod", "EXPENSE", 136400, "Global static asset delivery"),
    ("2026-11-14", "Committed Savings Rebate", "Compute-K8s", "prod", "CREDIT", 32000, "1-yr Compute Savings Plan discount"),
    ("2026-11-17", "OpenTelemetry Collector", "Observability", "staging", "EXPENSE", 89500, "Trace ingestion & metrics retention"),
    ("2026-11-20", "Load Test Sandbox Cluster", "Compute-K8s", "sandbox", "RESERVATION", 64000, "Pre-release stress test allocation"),
]


def seed_if_empty(db_path: str | Path) -> None:
    with get_connection(db_path) as conn:
        budget_count = conn.execute("SELECT COUNT(*) FROM cost_budgets").fetchone()[0]
        if budget_count == 0:
            conn.executemany(
                "INSERT INTO cost_budgets (cost_center, monthly_cap_cents) VALUES (?, ?)",
                DEFAULT_BUDGETS,
            )

        entry_count = conn.execute("SELECT COUNT(*) FROM ledger_entries").fetchone()[0]
        if entry_count == 0:
            conn.executemany(
                """
                INSERT INTO ledger_entries
                (recorded_date, vendor_service, cost_center, environment, entry_type, amount_cents, memo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                DEFAULT_ENTRIES,
            )
