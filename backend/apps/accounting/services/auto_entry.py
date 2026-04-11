"""
Auto-generated journal entry generators.

Provides specialised generators that create journal entries from
business transactions: sales invoices, purchase bills, payments,
payroll runs, and inventory adjustments.
"""

import logging
from abc import ABC, abstractmethod
from decimal import Decimal

from apps.accounting.models import Account
from apps.accounting.models.enums import JournalEntryType, JournalSource
from apps.accounting.services.journal_service import JournalEntryService

logger = logging.getLogger(__name__)


class EntryGenerationError(Exception):
    """Raised when auto-entry generation fails."""


class BalanceValidationError(EntryGenerationError):
    """Raised when generated lines do not balance."""


class AutoEntryGenerator(ABC):
    """
    Abstract base class for auto-generating journal entries.

    Subclasses must implement get_debit_lines() and get_credit_lines()
    to return lists of line dicts for the transaction.
    """

    def __init__(self, source_document):
        self.source = source_document

    @abstractmethod
    def get_debit_lines(self):
        """Return list of debit line dicts."""

    @abstractmethod
    def get_credit_lines(self):
        """Return list of credit line dicts."""

    def get_description(self):
        """Default description from source document."""
        return f"Auto-generated from {self.source}"

    def get_reference(self):
        """Default reference from source document."""
        return str(getattr(self.source, "reference_number", "") or getattr(self.source, "id", ""))

    def get_entry_source(self):
        """Override in subclasses to set the JournalSource."""
        return JournalSource.MANUAL

    def generate_entry(self, created_by=None):
        """
        Orchestrate entry generation.

        Returns:
            Created JournalEntry instance.

        Raises:
            EntryGenerationError: If generation fails.
            BalanceValidationError: If lines do not balance.
        """
        debit_lines = self.get_debit_lines()
        credit_lines = self.get_credit_lines()
        all_lines = debit_lines + credit_lines

        total_debit = sum(l.get("debit_amount", Decimal("0")) for l in all_lines)
        total_credit = sum(l.get("credit_amount", Decimal("0")) for l in all_lines)
        if total_debit != total_credit:
            raise BalanceValidationError(
                f"Generated entry does not balance: "
                f"DR={total_debit}, CR={total_credit}"
            )

        entry_date = getattr(self.source, "date", None) or getattr(self.source, "entry_date", None)
        if entry_date is None:
            from django.utils import timezone
            entry_date = timezone.now().date()

        entry = JournalEntryService.create_entry(
            entry_date=entry_date,
            lines_data=all_lines,
            description=self.get_description(),
            entry_type=JournalEntryType.AUTO,
            entry_source=self.get_entry_source(),
            reference=self.get_reference(),
            created_by=created_by,
        )

        logger.info(
            "Auto-generated entry %s from %s",
            entry.entry_number,
            self.get_entry_source(),
        )
        return entry


def _get_account(code):
    """Helper to look up an account by code."""
    try:
        return Account.objects.get(code=code, is_active=True)
    except Account.DoesNotExist:
        raise EntryGenerationError(f"Account with code {code} not found or inactive.")


class SalesEntryGenerator(AutoEntryGenerator):
    """Generate journal entries from sales invoices."""

    def get_entry_source(self):
        return JournalSource.SALES

    def get_description(self):
        ref = self.get_reference()
        return f"Sales invoice {ref}"

    def get_debit_lines(self):
        total = getattr(self.source, "total_amount", Decimal("0"))
        return [
            {
                "account": _get_account("1200"),
                "debit_amount": total,
                "credit_amount": Decimal("0"),
                "description": "Accounts Receivable",
            }
        ]

    def get_credit_lines(self):
        net = getattr(self.source, "net_amount", Decimal("0"))
        vat = getattr(self.source, "tax_amount", Decimal("0"))
        lines = [
            {
                "account": _get_account("4000"),
                "debit_amount": Decimal("0"),
                "credit_amount": net,
                "description": "Sales Revenue",
            }
        ]
        if vat > 0:
            lines.append(
                {
                    "account": _get_account("2150"),
                    "debit_amount": Decimal("0"),
                    "credit_amount": vat,
                    "description": "VAT Output",
                }
            )
        return lines


class PurchaseEntryGenerator(AutoEntryGenerator):
    """Generate journal entries from purchase bills."""

    def get_entry_source(self):
        return JournalSource.PURCHASE

    def get_description(self):
        ref = self.get_reference()
        return f"Purchase bill {ref}"

    def get_debit_lines(self):
        net = getattr(self.source, "net_amount", Decimal("0"))
        vat = getattr(self.source, "tax_amount", Decimal("0"))
        lines = [
            {
                "account": _get_account("1300"),
                "debit_amount": net,
                "credit_amount": Decimal("0"),
                "description": "Inventory / Expense",
            }
        ]
        if vat > 0:
            lines.append(
                {
                    "account": _get_account("1500"),
                    "debit_amount": vat,
                    "credit_amount": Decimal("0"),
                    "description": "VAT Input",
                }
            )
        return lines

    def get_credit_lines(self):
        total = getattr(self.source, "total_amount", Decimal("0"))
        return [
            {
                "account": _get_account("2000"),
                "debit_amount": Decimal("0"),
                "credit_amount": total,
                "description": "Accounts Payable",
            }
        ]


class PaymentEntryGenerator(AutoEntryGenerator):
    """Generate journal entries from payment transactions."""

    def get_entry_source(self):
        return JournalSource.BANKING

    def get_description(self):
        direction = getattr(self.source, "payment_type", "payment")
        ref = self.get_reference()
        return f"Payment {direction} {ref}"

    def get_debit_lines(self):
        amount = getattr(self.source, "amount", Decimal("0"))
        is_received = getattr(self.source, "payment_type", "received") == "received"

        if is_received:
            return [
                {
                    "account": _get_account("1100"),
                    "debit_amount": amount,
                    "credit_amount": Decimal("0"),
                    "description": "Bank Account",
                }
            ]
        else:
            return [
                {
                    "account": _get_account("2000"),
                    "debit_amount": amount,
                    "credit_amount": Decimal("0"),
                    "description": "Accounts Payable",
                }
            ]

    def get_credit_lines(self):
        amount = getattr(self.source, "amount", Decimal("0"))
        is_received = getattr(self.source, "payment_type", "received") == "received"

        if is_received:
            return [
                {
                    "account": _get_account("1200"),
                    "debit_amount": Decimal("0"),
                    "credit_amount": amount,
                    "description": "Accounts Receivable",
                }
            ]
        else:
            return [
                {
                    "account": _get_account("1100"),
                    "debit_amount": Decimal("0"),
                    "credit_amount": amount,
                    "description": "Bank Account",
                }
            ]


class PayrollEntryGenerator(AutoEntryGenerator):
    """
    Generate journal entries from payroll runs.

    Sri Lanka specific statutory deductions:
        - EPF: Employee 8% + Employer 12% = Total 20%
        - ETF: Employer 3%
        - PAYE: Progressive income tax
    """

    def get_entry_source(self):
        return JournalSource.PAYROLL

    def get_description(self):
        return f"Payroll run {self.get_reference()}"

    def _calculate_epf(self, gross):
        employee = gross * Decimal("0.08")
        employer = gross * Decimal("0.12")
        return employee, employer, employee + employer

    def _calculate_etf(self, gross):
        return gross * Decimal("0.03")

    def _calculate_paye(self, gross):
        paye = getattr(self.source, "paye_amount", None)
        if paye is not None:
            return paye
        return Decimal("0")

    def get_debit_lines(self):
        gross = getattr(self.source, "gross_salary", Decimal("0"))
        _, employer_epf, _ = self._calculate_epf(gross)
        etf = self._calculate_etf(gross)

        return [
            {
                "account": _get_account("5100"),
                "debit_amount": gross,
                "credit_amount": Decimal("0"),
                "description": "Salaries Expense",
            },
            {
                "account": _get_account("5101"),
                "debit_amount": employer_epf,
                "credit_amount": Decimal("0"),
                "description": "EPF Expense (Employer 12%)",
            },
            {
                "account": _get_account("5102"),
                "debit_amount": etf,
                "credit_amount": Decimal("0"),
                "description": "ETF Expense (Employer 3%)",
            },
        ]

    def get_credit_lines(self):
        gross = getattr(self.source, "gross_salary", Decimal("0"))
        employee_epf, employer_epf, total_epf = self._calculate_epf(gross)
        etf = self._calculate_etf(gross)
        paye = self._calculate_paye(gross)
        net_pay = gross - employee_epf - paye

        return [
            {
                "account": _get_account("2200"),
                "debit_amount": Decimal("0"),
                "credit_amount": total_epf,
                "description": "EPF Payable (Total 20%)",
            },
            {
                "account": _get_account("2201"),
                "debit_amount": Decimal("0"),
                "credit_amount": etf,
                "description": "ETF Payable (3%)",
            },
            {
                "account": _get_account("2210"),
                "debit_amount": Decimal("0"),
                "credit_amount": paye,
                "description": "PAYE Payable",
            },
            {
                "account": _get_account("2100"),
                "debit_amount": Decimal("0"),
                "credit_amount": net_pay,
                "description": "Net Salaries Payable",
            },
        ]


class InventoryEntryGenerator(AutoEntryGenerator):
    """Generate journal entries from inventory adjustments."""

    ADJUSTMENT_ACCOUNTS = {
        "WRITE_OFF": "5200",
        "LOSS_THEFT": "5201",
        "REVALUATION": "5202",
        "PHYSICAL_COUNT": "5203",
        "RETURN": "1300",
    }

    def get_entry_source(self):
        return JournalSource.INVENTORY

    def get_description(self):
        adj_type = getattr(self.source, "adjustment_type", "adjustment")
        return f"Inventory {adj_type} {self.get_reference()}"

    def _get_adjustment_account_code(self):
        adj_type = getattr(self.source, "adjustment_type", "PHYSICAL_COUNT")
        return self.ADJUSTMENT_ACCOUNTS.get(adj_type, "5203")

    def get_debit_lines(self):
        amount = abs(getattr(self.source, "total_value", Decimal("0")))
        is_increase = getattr(self.source, "total_value", Decimal("0")) > 0

        if is_increase:
            return [
                {
                    "account": _get_account("1300"),
                    "debit_amount": amount,
                    "credit_amount": Decimal("0"),
                    "description": "Inventory",
                }
            ]
        else:
            return [
                {
                    "account": _get_account(self._get_adjustment_account_code()),
                    "debit_amount": amount,
                    "credit_amount": Decimal("0"),
                    "description": "Inventory Adjustment Expense",
                }
            ]

    def get_credit_lines(self):
        amount = abs(getattr(self.source, "total_value", Decimal("0")))
        is_increase = getattr(self.source, "total_value", Decimal("0")) > 0

        if is_increase:
            return [
                {
                    "account": _get_account(self._get_adjustment_account_code()),
                    "debit_amount": Decimal("0"),
                    "credit_amount": amount,
                    "description": "Inventory Adjustment",
                }
            ]
        else:
            return [
                {
                    "account": _get_account("1300"),
                    "debit_amount": Decimal("0"),
                    "credit_amount": amount,
                    "description": "Inventory",
                }
            ]
