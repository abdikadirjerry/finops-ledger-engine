from src.models import CenterBudget, LedgerEntry, VALID_COST_CENTERS, VALID_ENVIRONMENTS


def compute_center_budgets(entries: list[LedgerEntry], caps: dict[str, int]) -> list[CenterBudget]:
    spent_map = {center: 0 for center in VALID_COST_CENTERS}
    for entry in entries:
        if entry.cost_center in spent_map:
            spent_map[entry.cost_center] += entry.signed_cents

    budgets: list[CenterBudget] = []
    for center in VALID_COST_CENTERS:
        budgets.append(
            CenterBudget(
                cost_center=center,
                monthly_cap_cents=caps.get(center, 0),
                spent_cents=max(0, spent_map[center]),
            )
        )
    return budgets


def compute_environment_breakdown(entries: list[LedgerEntry]) -> list[dict]:
    totals = {env: 0 for env in VALID_ENVIRONMENTS}
    for entry in entries:
        if entry.environment in totals:
            totals[entry.environment] += entry.signed_cents

    grand_total = sum(max(0, val) for val in totals.values())
    breakdown = []
    for env in VALID_ENVIRONMENTS:
        cents = max(0, totals[env])
        share = round((cents / grand_total) * 100.0, 1) if grand_total > 0 else 0.0
        breakdown.append({
            "environment": env,
            "cents": cents,
            "formatted": f"${cents / 100.0:,.2f}",
            "share_pct": share,
        })
    return breakdown


def compute_executive_kpis(entries: list[LedgerEntry], budgets: list[CenterBudget]) -> dict:
    net_spend_cents = sum(e.signed_cents for e in entries)
    total_credits_cents = sum(e.amount_cents for e in entries if e.entry_type == "CREDIT")
    total_cap_cents = sum(b.monthly_cap_cents for b in budgets)
    remaining_cents = total_cap_cents - net_spend_cents
    overrun_centers = sum(1 for b in budgets if b.utilization_pct >= 90.0)

    return {
        "net_spend_formatted": f"${net_spend_cents / 100.0:,.2f}",
        "total_cap_formatted": f"${total_cap_cents / 100.0:,.2f}",
        "remaining_formatted": f"${remaining_cents / 100.0:,.2f}",
        "credits_formatted": f"${total_credits_cents / 100.0:,.2f}",
        "is_over_budget": remaining_cents < 0,
        "alert_centers_count": overrun_centers,
        "entry_count": len(entries),
    }
