import tempfile
import unittest
from pathlib import Path
from src.analytics import (
    compute_center_budgets,
    compute_environment_breakdown,
    compute_executive_kpis,
)
from src.ledger_repo import FinOpsRepository


class TestFinOpsAnalytics(unittest.TestCase):
    def test_credits_reduce_net_spend_and_update_variance(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = FinOpsRepository(str(Path(tmpdir) / "analytics.db"))
            repo.update_budget_cap("Observability", "1000.00")
            repo.add_entry("2026-11-21", "Grafana Credit", "Observability", "staging", "CREDIT", "200.00", "Promo credit")

            entries = repo.list_entries()
            budgets = compute_center_budgets(entries, repo.get_budget_caps())
            obs_budget = next(b for b in budgets if b.cost_center == "Observability")

            # Seeded $895.00 - $200.00 credit = $695.00 (69500 cents)
            self.assertEqual(obs_budget.spent_cents, 69500)
            self.assertEqual(obs_budget.utilization_pct, 69.5)

            kpis = compute_executive_kpis(entries, budgets)
            self.assertEqual(kpis["total_cap_formatted"], "$11,350.00")
            env_stats = compute_environment_breakdown(entries)
            self.assertEqual(len(env_stats), 3)


if __name__ == "__main__":
    unittest.main()
