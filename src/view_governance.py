import html
from src.models import CenterBudget


def render_budgets_tab(budgets: list[CenterBudget]) -> str:
    rows = []
    for b in budgets:
        cap_dollars = f"{b.monthly_cap_cents / 100.0:.2f}"
        rem_dollars = f"${b.remaining_cents / 100.0:,.2f}"
        rem_cls = "text-crimson" if b.remaining_cents < 0 else "text-emerald"
        rows.append(
            f"""
            <tr>
              <td><strong>{html.escape(b.cost_center)}</strong></td>
              <td class="mono">${b.spent_cents / 100.0:,.2f}</td>
              <td class="mono {rem_cls}"><strong>{rem_dollars}</strong></td>
              <td class="mono">{b.utilization_pct}%</td>
              <td>
                <form method="POST" action="/budgets/update" style="display:flex; gap:0.5rem;">
                  <input type="hidden" name="cost_center" value="{html.escape(b.cost_center)}" />
                  <input type="text" name="cap_dollars" value="{cap_dollars}" class="mono"
                         style="width:120px; padding:0.4rem; border:1px solid #d5e0dc; border-radius:6px;" required />
                  <button type="submit" class="btn-primary">Update Cap</button>
                </form>
              </td>
            </tr>
            """
        )

    return f"""
    <section class="card">
      <div class="section-head">
        <h2>Monthly Cost Center Cap Governance</h2>
        <span style="font-size:0.8rem; color:#52665f;">Changes recalculate variance across all reports immediately</span>
      </div>
      <table class="ledger-table">
        <thead>
          <tr>
            <th>Cost Center</th><th>Current Net Spend</th><th>Remaining Allowance</th>
            <th>Utilization</th><th>Monthly Cap (USD)</th>
          </tr>
        </thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </section>
    """


def render_audit_tab(sample_json: str) -> str:
    return f"""
    <section class="card">
      <div class="section-head">
        <h2>Financial Audit &amp; Statement Exports</h2>
        <div style="display:flex; gap:0.6rem;">
          <a href="/export/ledger.csv" class="btn-primary">Download RFC-4180 CSV</a>
          <a href="/api/audit" class="btn-outline" target="_blank">Open Raw JSON API</a>
        </div>
      </div>
      <p style="font-size:0.85rem; color:#52665f; margin-bottom:1rem;">
        Live serialized snapshot of your general ledger, budget caps, and executive KPIs:
      </p>
      <pre class="mono" style="background:#11241e; color:#d1fae5; padding:1rem; border-radius:8px; overflow-x:auto; font-size:0.8rem;">{html.escape(sample_json)}</pre>
    </section>
    """
