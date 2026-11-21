import html
from src.models import CenterBudget, LedgerEntry


def render_overview_tab(
    budgets: list[CenterBudget],
    env_breakdown: list[dict],
    recent_entries: list[LedgerEntry],
) -> str:
    budget_bars = []
    for b in budgets:
        pct = min(100.0, b.utilization_pct)
        bar_cls = "danger" if b.utilization_pct >= 95 else ("warn" if b.utilization_pct >= 80 else "")
        budget_bars.append(
            f"""
            <div class="budget-row">
              <div class="budget-meta">
                <strong>{html.escape(b.cost_center)}</strong>
                <span class="mono">${b.spent_cents / 100:,.2f} /${b.monthly_cap_cents / 100:,.2f} ({b.utilization_pct}%)</span>
              </div>
              <div class="progress-track">
                <div class="progress-fill {bar_cls}" style="width: {pct}%"></div>
              </div>
            </div>
            """
        )

    env_rows = []
    for item in env_breakdown:
        env_rows.append(
            f"""
            <tr>
              <td><strong class="mono">{html.escape(item['environment'].upper())}</strong></td>
              <td class="mono">{html.escape(item['formatted'])}</td>
              <td class="mono">{item['share_pct']}%</td>
            </tr>
            """
        )

    recent_rows = []
    for e in recent_entries[:5]:
        amt_cls = "text-emerald" if e.entry_type == "CREDIT" else ""
        recent_rows.append(
            f"""
            <tr>
              <td class="mono">{html.escape(e.recorded_date)}</td>
              <td><strong>{html.escape(e.vendor_service)}</strong></td>
              <td>{html.escape(e.cost_center)}</td>
              <td><span class="pill pill-{html.escape(e.entry_type)}">{html.escape(e.entry_type)}</span></td>
              <td class="mono {amt_cls}"><strong>{html.escape(e.formatted_dollars)}</strong></td>
            </tr>
            """
        )

    return f"""
    <div class="two-col-layout">
      <section class="card">
        <div class="section-head">
          <h2>Cost Center Budget Utilization</h2>
          <a href="/?tab=budgets" class="btn-outline">Adjust Caps</a>
        </div>
        {''.join(budget_bars)}
      </section>

      <section class="card">
        <div class="section-head">
          <h2>Spend by Environment</h2>
          <span class="mono" style="font-size:0.75rem; color:#52665f;">MTD Allocation</span>
        </div>
        <table class="ledger-table">
          <thead>
            <tr><th>Environment</th><th>Net Spend</th><th>Share</th></tr>
          </thead>
          <tbody>{''.join(env_rows)}</tbody>
        </table>
      </section>
    </div>

    <section class="card">
      <div class="section-head">
        <h2>Latest Ledger Postings</h2>
        <a href="/?tab=journal" class="btn-primary">+ Post Journal Entry</a>
      </div>
      <table class="ledger-table">
        <thead>
          <tr><th>Date</th><th>Service / Vendor</th><th>Cost Center</th><th>Type</th><th>Amount</th></tr>
        </thead>
        <tbody>{''.join(recent_rows)}</tbody>
      </table>
    </section>
    """
