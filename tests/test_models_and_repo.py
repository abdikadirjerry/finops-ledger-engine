import tempfile
import unittest
from pathlib import Path
from src.ledger_repo import FinOpsRepository, parse_dollars_to_cents


class TestFinOpsRepository(unittest.TestCase):
    def test_exact_decimal_cents_conversion(self):
        self.assertEqual(parse_dollars_to_cents("$1,249.99"), 124999)
        self.assertEqual(parse_dollars_to_cents("42.5"), 4250)
        self.assertEqual(parse_dollars_to_cents("invalid"), 100)

    def test_add_filter_and_delete_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = FinOpsRepository(str(Path(tmpdir) / "finops.db"))
            new_id = repo.add_entry(
                "2026-11-21",
                "Cloudflare Workers",
                "Network-CDN",
                "prod",
                "EXPENSE",
                "125.00",
                "Edge routing surcharge",
            )
            cdn_entries = repo.list_entries(center_filter="Network-CDN", env_filter="prod")
            self.assertTrue(any(e.id == new_id and e.amount_cents == 12500 for e in cdn_entries))

            repo.delete_entry(new_id)
            after_delete = repo.list_entries(center_filter="Network-CDN")
            self.assertFalse(any(e.id == new_id for e in after_delete))


if __name__ == "__main__":
    unittest.main()
