from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from src.analytics import (
    compute_center_budgets,
    compute_environment_breakdown,
    compute_executive_kpis,
)
from src.exporters import export_audit_json, export_entries_csv
from src.ledger_repo import FinOpsRepository
from src.view_governance import render_audit_tab, render_budgets_tab
from src.view_journal import render_journal_tab
from src.view_layout import render_shell
from src.view_overview import render_overview_tab

REPO = FinOpsRepository("data/finops_ledger.db")
STATIC_DIR = Path(__file__).parent / "static"


class VerdantLedgerHandler(BaseHTTPRequestHandler):
    def _send_bytes(self, payload: bytes, content_type: str, status: int = 200, extra_headers: dict | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(payload)

    def _redirect(self, location: str) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/static/finops.css":
            self._send_bytes((STATIC_DIR / "finops.css").read_bytes(), "text/css; charset=utf-8")
            return

        all_entries = REPO.list_entries()
        caps = REPO.get_budget_caps()
        budgets = compute_center_budgets(all_entries, caps)
        kpis = compute_executive_kpis(all_entries, budgets)

        if parsed.path == "/export/ledger.csv":
            csv_text = export_entries_csv(all_entries)
            self._send_bytes(
                csv_text.encode("utf-8"),
                "text/csv; charset=utf-8",
                extra_headers={"Content-Disposition": 'attachment; filename="verdant_finops_ledger.csv"'},
            )
            return

        if parsed.path == "/api/audit":
            json_text = export_audit_json(all_entries, budgets, kpis)
            self._send_bytes(json_text.encode("utf-8"), "application/json; charset=utf-8")
            return

        if parsed.path == "/":
            tab = params.get("tab", ["overview"])[0]
            if tab == "journal":
                center_f = params.get("center", ["ALL"])[0]
                env_f = params.get("env", ["ALL"])[0]
                filtered = REPO.list_entries(center_filter=center_f, env_filter=env_f)
                body = render_journal_tab(filtered, center_f, env_f)
            elif tab == "budgets":
                body = render_budgets_tab(budgets)
            elif tab == "audit":
                body = render_audit_tab(export_audit_json(all_entries, budgets, kpis))
            else:
                tab = "overview"
                env_breakdown = compute_environment_breakdown(all_entries)
                body = render_overview_tab(budgets, env_breakdown, all_entries)

            html_page = render_shell(tab, kpis, body)
            self._send_bytes(html_page.encode("utf-8"), "text/html; charset=utf-8")
            return

        self._send_bytes(b"404 Not Found", "text/plain; charset=utf-8", 404)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode("utf-8"))

        if self.path == "/entries/create":
            REPO.add_entry(
                recorded_date=form.get("recorded_date", [""])[0],
                vendor_service=form.get("vendor_service", [""])[0],
                cost_center=form.get("cost_center", ["Compute-K8s"])[0],
                environment=form.get("environment", ["prod"])[0],
                entry_type=form.get("entry_type", ["EXPENSE"])[0],
                raw_amount_dollars=form.get("amount", ["1.00"])[0],
                memo=form.get("memo", [""])[0],
            )
            self._redirect("/?tab=journal")
            return

        if self.path == "/entries/delete":
            entry_id = int(form.get("id", ["0"])[0])
            REPO.delete_entry(entry_id)
            self._redirect("/?tab=journal")
            return

        if self.path == "/budgets/update":
            center = form.get("cost_center", [""])[0]
            cap_dollars = form.get("cap_dollars", ["100.00"])[0]
            REPO.update_budget_cap(center, cap_dollars)
            self._redirect("/?tab=budgets")
            return

        self._send_bytes(b"404 Not Found", "text/plain; charset=utf-8", 404)


def main(host: str = "127.0.0.1", port: int = 8098) -> None:
    server = ThreadingHTTPServer((host, port), VerdantLedgerHandler)
    print(f"[*] VerdantLedger FinOps Engine running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Stopping VerdantLedger server...")
        server.server_close()


if __name__ == "__main__":
    main()
