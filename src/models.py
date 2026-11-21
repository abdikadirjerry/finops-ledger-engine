from dataclasses import dataclass

VALID_COST_CENTERS = ("Compute-K8s", "Database-RDS", "Object-Storage", "Network-CDN", "Observability")
VALID_ENVIRONMENTS = ("prod", "staging", "sandbox")
VALID_ENTRY_TYPES = ("EXPENSE", "CREDIT", "RESERVATION")


@dataclass(frozen=True)
class LedgerEntry:
    id: int
    recorded_date: str
    vendor_service: str
    cost_center: str
    environment: str
    entry_type: str
    amount_cents: int
    memo: str

    @property
    def signed_cents(self) -> int:
        return -self.amount_cents if self.entry_type == "CREDIT" else self.amount_cents

    @property
    def formatted_dollars(self) -> str:
        dollars = abs(self.signed_cents) / 100.0
        prefix = "-" if self.signed_cents < 0 else ""
        return f"{prefix}${dollars:,.2f}"


@dataclass(frozen=True)
class CenterBudget:
    cost_center: str
    monthly_cap_cents: int
    spent_cents: int

    @property
    def utilization_pct(self) -> float:
        if self.monthly_cap_cents <= 0:
            return 0.0
        return round((self.spent_cents / self.monthly_cap_cents) * 100.0, 1)

    @property
    def remaining_cents(self) -> int:
        return self.monthly_cap_cents - self.spent_cents
