"""PayrollHistory model for audit trail of all payroll actions."""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin
from apps.payroll.constants import HistoryAction


class PayrollHistory(UUIDMixin, models.Model):
    """Audit trail recording every significant action on a payroll run."""

    payroll_run = models.ForeignKey(
        "payroll.PayrollRun",
        on_delete=models.CASCADE,
        related_name="history",
    )
    action = models.CharField(
        max_length=20,
        choices=HistoryAction.choices,
        db_index=True,
    )
    previous_status = models.CharField(max_length=20, blank=True, default="")
    new_status = models.CharField(max_length=20, blank=True, default="")
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payroll_history_actions",
    )
    performed_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, default="")
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "payroll_history"
        ordering = ["-performed_at"]
        verbose_name = "Payroll History"
        verbose_name_plural = "Payroll Histories"
        indexes = [
            models.Index(
                fields=["payroll_run", "-performed_at"],
                name="idx_payhistory_run_date",
            ),
            models.Index(
                fields=["performed_by"],
                name="idx_payhistory_user",
            ),
        ]

    def __str__(self):
        return f"{self.get_action_display()} by {self.performed_by} at {self.performed_at}"
