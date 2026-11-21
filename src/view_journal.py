import html
from datetime import date
from src.models import (
    LedgerEntry,
    VALID_COST_CENTERS,
    VALID_ENTRY_TYPES,
    VALID_ENVIRONMENTS,
)


def render_journal_tab(
    entries: list[LedgerEntry],
    center_filter: str,
    env_filter: str,
) -> str:
    center_options = "".join(
        f'<option value="{c}" {"selected" if c == center_filter else ""}>{c}</option>'
        for c in VALID_COST_CENTERS
    )
    env_options = "".join(
        f'<option value="{env}" {"selected" if env == env_filter else ""}>{env}</option>'
        for env in VALID_ENVIRONMENTS
    )
    type_options = "".join(f'<option value="{t}">{t}</option>' for t in VALID_ENTRY_TYPES)

    rows = []
    for e in entries:
        amt_cls = "text-emerald" if e.entry_type == "CREDIT" else ""
        rows.append(
            f"""
            <tr>
              <td class="mono">#{e.id}</td>
              <td class="mono">{html.escape(e.recorded_date)}</td>
              <td>
                <strong>{html.escape(e.vendor_service)}</strong>
                <div style="font-size:0.75rem; color:#52665f;">{html.escape(e.memo)}</div>
              </td>
              <td>{html.escape(e.cost_center)}</td>
              <td class="mono">{html.escape(e.environment)}</td>
              <td><span class="pill pill-{html.escape(e.entry_type)}">{html.escape(e.entry_type)}</span></td>
              <td class="mono {amt_cls}"><strong>{html.escape(e.formatted_dollars)}</strong></td>
              <td>
                <form method="POST" action="/entries/delete">
                  <input type="hidden" name="id" value="{e.id}" />
                  <button type="submit" class="btn-outline" style="color:#b91c1c;">Void</button>
                </form>
              </td>
            </tr>
            """
        )

    return f"""
    <section class="card">
      <div class="section-head">
        <h2>Post New Cloud Cost or Rebate Entry</h2>
      </div>
      <form class="entry-form" method="POST" action="/entries/create">
        <input type="date" name="recorded_date" value="{date.today().isoformat()}" required />
        <input type="text" name="vendor_service" placeholder="Vendor / Resource (e.g., AWS RDS Read Replica)" required />
        <select name="cost_center">{''.join(f'<option value="{c}">{c}</option>' for c in VALID_COST_CENTERS)}</select>
        <select name="environment">{''.join(f'<option value="{env}">{env}</option>' for env in VALID_ENVIRONMENTS)}</select>
        <select name="entry_type">{type_options}</select>
        <input type="text" name="amount" placeholder="Amount USD (e.g., 425.50)" required />
        <input type="text" name="memo" placeholder="Audit memo or invoice reference" style="grid-column: span 2;" required />
        <button type="submit" class="btn-primary">Record Ledger Entry</button>
      </form>
    </section>

    <section class="card">
      <div class="section-head">
        <h2>General FinOps Journal ({len(entries)} records)</h2>
        <form method="GET" action="/" style="display:flex; gap:0.5rem; align-items:center;">
          <input type="hidden" name="tab" value="journal" />
          <select name="center" style="padding:0.4rem; border-radius:6px; border:1px solid #d5e0dc;">
            <option value="ALL">All Cost Centers</option>
            {center_options}
          </select>
          <select name="env" style="padding:0.4rem; border-radius:6px; border:1px solid #d5e0dc;">
            <option value="ALL">All Environments</option>
            {env_options}
          </select>
          <button type="submit" class="btn-outline">Filter</button>
        </form>
      </div>

      <table class="ledger-table">
        <thead>
          <tr>
            <th>ID</th><th>Date</th><th>Service &amp; Memo</th><th>Cost Center</th>
            <th>Env</th><th>Type</th><th>Signed Amount</th><th>Action</th>
          </tr>
        </thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </section>
    """
