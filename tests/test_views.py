import tempfile
import unittest
from pathlib import Path
from src.analytics import compute_center_budgets, compute_executive_kpis
from src.ledger_repo import FinOpsRepository
from src.view_governance import render_budgets_tab
from src.view_layout import render_shell


class TestFinOpsViews(unittest.TestCase):
    def test_html_rendering_and_xss_safety(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = FinOpsRepository(str(Path(tmpdir) / "views.db"))
            repo.add_entry("2026-11-21", "<script>alert(1)</script>", "Compute-K8s", "prod", "EXPENSE", "10.00", "XSS test")
            entries = repo.list_entries()
            budgets = compute_center_budgets(entries, repo.get_budget_caps())
            kpis = compute_executive_kpis(entries, budgets)

            page = render_shell("budgets", kpis, render_budgets_tab(budgets))
            self.assertIn("VERDANT<span>LEDGER</span>", page)
            self.assertNotIn("<script>alert(1)</script>", page)


if __name__ == "__main__":
    unittest.main()
