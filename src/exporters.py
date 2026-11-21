import csv
import io
import json
from src.models import CenterBudget, LedgerEntry


def export_entries_csv(entries: list[LedgerEntry]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "id",
        "recorded_date",
        "vendor_service",
        "cost_center",
        "environment",
        "entry_type",
        "signed_amount_usd",
        "memo",
    ])
    for item in entries:
        writer.writerow([
            item.id,
            item.recorded_date,
            item.vendor_service,
            item.cost_center,
            item.environment,
            item.entry_type,
            f"{item.signed_cents / 100.0:.2f}",
            item.memo,
        ])
    return buffer.getvalue()


def export_audit_json(entries: list[LedgerEntry], budgets: list[CenterBudget], kpis: dict) -> str:
    payload = {
        "kpis": kpis,
        "budgets": [
            {
                "cost_center": b.cost_center,
                "monthly_cap_usd": round(b.monthly_cap_cents / 100.0, 2),
                "net_spent_usd": round(b.spent_cents / 100.0, 2),
                "utilization_pct": b.utilization_pct,
            }
            for b in budgets
        ],
        "entries": [
            {
                "id": e.id,
                "recorded_date": e.recorded_date,
                "vendor_service": e.vendor_service,
                "cost_center": e.cost_center,
                "environment": e.environment,
                "entry_type": e.entry_type,
                "signed_amount_usd": round(e.signed_cents / 100.0, 2),
                "memo": e.memo,
            }
            for e in entries
        ],
    }
    return json.dumps(payload, indent=2)
