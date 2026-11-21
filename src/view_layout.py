import html


def render_shell(active_tab: str, kpis: dict, body_html: str) -> str:
    tabs = [
        ("overview", "Overview & Budgets"),
        ("journal", "Journal Entries"),
        ("budgets", "Cap Governance"),
        ("audit", "CSV & Audit Export"),
    ]
    nav_links = []
    for slug, label in tabs:
        cls = "active" if slug == active_tab else ""
        nav_links.append(f'<a href="/?tab={slug}" class="{cls}">{label}</a>')

    rem_class = "text-crimson" if kpis["is_over_budget"] else "text-emerald"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>VerdantLedger // FinOps Cost &amp; Budget Engine</title>
  <link rel="stylesheet" href="/static/finops.css" />
</head>
<body>
  <header class="topbar">
    <div class="brand">VERDANT<span>LEDGER</span> // CLOUD FINOPS &amp; DOUBLE-ENTRY BUDGETS</div>
    <nav class="nav-tabs">{''.join(nav_links)}</nav>
  </header>

  <main class="container">
    <section class="kpi-grid">
      <div class="card">
        <div class="kpi-label">Net Cloud Spend (MTD)</div>
        <div class="kpi-value">{html.escape(kpis['net_spend_formatted'])}</div>
      </div>
      <div class="card">
        <div class="kpi-label">Monthly Budget Cap</div>
        <div class="kpi-value text-emerald">{html.escape(kpis['total_cap_formatted'])}</div>
      </div>
      <div class="card">
        <div class="kpi-label">Remaining Variance</div>
        <div class="kpi-value {rem_class}">{html.escape(kpis['remaining_formatted'])}</div>
      </div>
      <div class="card">
        <div class="kpi-label">Applied Credits &amp; Rebates</div>
        <div class="kpi-value text-emerald">{html.escape(kpis['credits_formatted'])}</div>
      </div>
    </section>

    {body_html}
  </main>
</body>
</html>"""
