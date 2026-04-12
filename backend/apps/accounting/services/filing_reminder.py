"""
Filing reminder service.

Calculates Sri Lankan tax filing deadlines, determines reminder
urgency, and sends email notifications for upcoming/overdue returns.

Due-date rules
--------------
- VAT:  20th of the following month (IRD)
- PAYE: 15th of the following month (IRD)
- EPF:  Last business day of the following month (CBSL)
- ETF:  Last business day of the following month (ETF Board)
"""

import calendar
import logging
from datetime import date, datetime, time, timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from apps.accounting.models.tax_period import TaxPeriodRecord
from apps.accounting.tax.enums import FilingStatus, TaxType

logger = logging.getLogger(__name__)

REMINDER_SCHEDULE_DAYS = [7, 3, 1, 0]


class FilingReminderService:
    """Centralised tax filing deadline logic."""

    def __init__(self, tenant=None):
        self.tenant = tenant

    # ── Pending filings ─────────────────────────────────────────────
    def get_pending_filings(self, days_ahead=30):
        """Return TaxPeriodRecords that have not been filed yet."""
        cutoff = timezone.now().date() + timedelta(days=days_ahead)
        qs = TaxPeriodRecord.objects.filter(
            filing_status__in=[FilingStatus.PENDING, FilingStatus.GENERATED],
            due_date__lte=cutoff,
            is_active=True,
        ).select_related("tax_configuration").order_by("due_date")
        return qs

    # ── Due-date router ─────────────────────────────────────────────
    def calculate_due_date(self, tax_type, period_start):
        """Route to the correct deadline calculator."""
        if tax_type == TaxType.VAT:
            return self.calculate_vat_due_date(period_start)
        if tax_type == TaxType.PAYE:
            return self.calculate_paye_due_date(period_start)
        if tax_type == TaxType.EPF:
            return self.calculate_epf_due_date(period_start)
        if tax_type == TaxType.ETF:
            return self.calculate_etf_due_date(period_start)
        raise ValueError(f"Unknown tax type: {tax_type}")

    # ── VAT: 20th of following month ────────────────────────────────
    def calculate_vat_due_date(self, period_start):
        year, month = period_start.year, period_start.month
        month += 1
        if month > 12:
            month = 1
            year += 1
        due = datetime.combine(date(year, month, 20), time(23, 59, 59))
        due = self._adjust_forward_to_weekday(due)
        return timezone.make_aware(due) if timezone.is_naive(due) else due

    # ── PAYE: 15th of following month ───────────────────────────────
    def calculate_paye_due_date(self, period_start):
        year, month = period_start.year, period_start.month
        month += 1
        if month > 12:
            month = 1
            year += 1
        due = datetime.combine(date(year, month, 15), time(23, 59, 59))
        due = self._adjust_forward_to_weekday(due)
        return timezone.make_aware(due) if timezone.is_naive(due) else due

    # ── EPF: last business day of following month ───────────────────
    def calculate_epf_due_date(self, period_start):
        year, month = period_start.year, period_start.month
        month += 1
        if month > 12:
            month = 1
            year += 1
        last_day = calendar.monthrange(year, month)[1]
        due = datetime.combine(date(year, month, last_day), time(23, 59, 59))
        due = self._adjust_backward_to_weekday(due)
        return timezone.make_aware(due) if timezone.is_naive(due) else due

    # ── ETF: same rule as EPF ───────────────────────────────────────
    def calculate_etf_due_date(self, period_start):
        return self.calculate_epf_due_date(period_start)

    # ── Weekend helpers ─────────────────────────────────────────────
    @staticmethod
    def _adjust_forward_to_weekday(dt):
        """Move Saturday/Sunday forward to Monday."""
        wd = dt.weekday()
        if wd == 5:
            return dt + timedelta(days=2)
        if wd == 6:
            return dt + timedelta(days=1)
        return dt

    @staticmethod
    def _adjust_backward_to_weekday(dt):
        """Move Saturday/Sunday backward to Friday."""
        wd = dt.weekday()
        if wd == 5:
            return dt - timedelta(days=1)
        if wd == 6:
            return dt - timedelta(days=2)
        return dt

    # ── Urgency ─────────────────────────────────────────────────────
    @staticmethod
    def get_urgency_level(due_date):
        today = timezone.now().date()
        if hasattr(due_date, "date"):
            due_date = due_date.date()
        remaining = (due_date - today).days
        if remaining < 0:
            return "overdue"
        if remaining <= 1:
            return "urgent"
        if remaining <= 3:
            return "warning"
        if remaining <= 7:
            return "upcoming"
        return "normal"

    @staticmethod
    def get_days_remaining(due_date):
        today = timezone.now().date()
        if hasattr(due_date, "date"):
            due_date = due_date.date()
        return (due_date - today).days

    # ── Reminder schedule ───────────────────────────────────────────
    @staticmethod
    def get_reminder_schedule():
        return list(REMINDER_SCHEDULE_DAYS)

    @classmethod
    def should_send_reminder(cls, due_date, last_reminder_date=None):
        days = cls.get_days_remaining(due_date)
        if days in REMINDER_SCHEDULE_DAYS or days < 0:
            if last_reminder_date and last_reminder_date == timezone.now().date():
                return False
            return True
        return False

    # ── Email ───────────────────────────────────────────────────────
    def send_reminder_email(self, reminder_data):
        """Send a filing-deadline reminder email.

        Args:
            reminder_data: dict with keys tax_type, period, due_date,
                           days_remaining, urgency.

        Returns:
            True on success, False on failure.
        """
        urgency = reminder_data.get("urgency", "normal")
        tax_type = reminder_data.get("tax_type", "TAX")
        days = reminder_data.get("days_remaining", 0)

        subject_map = {
            "overdue": f"URGENT: Tax Filing Overdue - {tax_type}",
            "urgent": f"Tax Filing Due Tomorrow - {tax_type}",
            "warning": f"Tax Filing Due in {days} Days - {tax_type}",
        }
        subject = subject_map.get(urgency, f"Tax Filing Reminder - {tax_type}")

        plain_body = (
            f"Dear Finance Team,\n\n"
            f"Tax Type: {tax_type}\n"
            f"Period: {reminder_data.get('period', '')}\n"
            f"Due Date: {reminder_data.get('due_date', '')}\n"
            f"Days Remaining: {days}\n"
            f"Status: {urgency.upper()}\n\n"
            f"Please file before the deadline to avoid penalties.\n\n"
            f"— ERP Tax Reporting Module"
        )

        try:
            html_body = render_to_string(
                "emails/tax_filing_reminder.html", reminder_data
            )
        except Exception:
            html_body = None

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")
        recipients = getattr(settings, "FINANCE_TEAM_EMAILS", [])
        if not recipients:
            logger.warning("No FINANCE_TEAM_EMAILS configured; skipping reminder.")
            return False

        try:
            msg = EmailMultiAlternatives(subject, plain_body, from_email, recipients)
            if html_body:
                msg.attach_alternative(html_body, "text/html")
            msg.send()
            logger.info("Sent %s reminder for %s", urgency, tax_type)
            return True
        except Exception:
            logger.exception("Failed to send %s reminder for %s", urgency, tax_type)
            return False

    # ── Dashboard widget data ───────────────────────────────────────
    def get_widget_data(self):
        """Return JSON-friendly dict for the dashboard widget."""
        pending = self.get_pending_filings(days_ahead=30)

        filings = []
        counts = {"overdue": 0, "urgent": 0, "warning": 0, "upcoming": 0}

        for period in pending:
            urgency = self.get_urgency_level(period.due_date)
            days = self.get_days_remaining(period.due_date)
            filings.append(
                {
                    "period_id": str(period.pk),
                    "tax_type": period.tax_type,
                    "period": f"{period.year}/{period.period_number:02d}",
                    "due_date": period.due_date.isoformat(),
                    "days_remaining": days,
                    "urgency": urgency,
                    "status": "OVERDUE" if days < 0 else "PENDING",
                }
            )
            if urgency in counts:
                counts[urgency] += 1

        from apps.accounting.models.tax_submission import TaxSubmission

        recent_qs = TaxSubmission.objects.order_by("-submitted_at")[:5]
        recent = [
            {
                "tax_type": s.tax_period.tax_type,
                "period": f"{s.tax_period.year}/{s.tax_period.period_number:02d}",
                "submitted_at": s.submitted_at.isoformat(),
                "status": s.get_status_display(),
            }
            for s in recent_qs.select_related("tax_period")
        ]

        return {
            "pending_filings": filings,
            "summary": {
                "pending_count": len(filings),
                **counts,
            },
            "recent_submissions": recent,
            "last_updated": timezone.now().isoformat(),
        }
