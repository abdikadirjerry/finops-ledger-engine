import csv
import io
import json
import tempfile
import unittest
from pathlib import Path
from src.analytics import compute_center_budgets, compute_executive_kpis
from src.exporters import export_audit_json, export_entries_csv
from src.ledger_repo import FinOpsRepository


class TestFinOpsExporters(unittest.TestCase):
    def test_csv_and_json_export_integrity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = FinOpsRepository(str(Path(tmpdir) / "export.db"))
            entries = repo.list_entries()
            budgets = compute_center_budgets(entries, repo.get_budget_caps())
            kpis = compute_executive_kpis(entries, budgets)

            csv_output = export_entries_csv(entries)
            rows = list(csv.reader(io.StringIO(csv_output)))
            self.assertEqual(rows[0][0], "id")
            self.assertEqual(len(rows) - 1, len(entries))

            parsed_json = json.loads(export_audit_json(entries, budgets, kpis))
            self.assertEqual(len(parsed_json["budgets"]), 5)
            self.assertIn("net_spend_formatted", parsed_json["kpis"])


if __name__ == "__main__":
    unittest.main()
