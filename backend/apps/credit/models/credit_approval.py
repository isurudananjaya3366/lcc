"""
CreditApprovalWorkflow model for credit approval requests.

Tracks credit approval requests with request details,
review status, and automated decision logic.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.credit.constants import ApprovalStatus, RequestType, RequestPriority


class CreditApprovalWorkflow(UUIDMixin, TimestampMixin, models.Model):
    """
    Credit approval request tracking.

    Manages the lifecycle of credit limit requests from submission
    through review to approval or rejection.
    """

    # ── Relationships ───────────────────────────────────────────────
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="credit_approvals",
    )
    credit_account = models.ForeignKey(
        "credit.CustomerCredit",
        on_delete=models.CASCADE,
        related_name="approval_requests",
        null=True,
        blank=True,
    )

    # ── Request Fields ──────────────────────────────────────────────
    requested_credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Requested credit limit (LKR).",
    )
    request_type = models.CharField(
        max_length=20,
        choices=RequestType.choices,
        default=RequestType.NEW_ACCOUNT,
        help_text="Type of credit request.",
    )
    request_reason = models.TextField(
        blank=True,
        default="",
        help_text="Reason for credit request.",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="credit_requests_made",
        help_text="User who submitted the request.",
    )
    requested_at = models.DateTimeField(
        auto_now_add=True,
    )

    # ── Status & Review Fields ──────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_credit_approvals",
        help_text="User who reviewed the request.",
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    decision_notes = models.TextField(
        blank=True,
        default="",
        help_text="Manager's notes on approval decision.",
    )

    # ── Additional Tracking (Task 15) ──────────────────────────────
    previous_credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Previous credit limit (for limit changes).",
    )
    supporting_documents = models.JSONField(
        default=list,
        blank=True,
        help_text="List of supporting document references.",
    )
    is_auto_approved = models.BooleanField(
        default=False,
        help_text="Whether this was auto-approved.",
    )
    auto_approval_reason = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Reason for auto-approval.",
    )
    priority = models.CharField(
        max_length=10,
        choices=RequestPriority.choices,
        default=RequestPriority.MEDIUM,
        help_text="Request priority.",
    )

    class Meta:
        verbose_name = "Credit Approval Request"
        verbose_name_plural = "Credit Approval Requests"
        db_table = "credit_approval_workflow"
        ordering = ["-requested_at"]
        indexes = [
            models.Index(
                fields=["status", "-requested_at"],
                name="credit_approval_status_idx",
            ),
            models.Index(
                fields=["customer", "status"],
                name="credit_approval_cust_idx",
            ),
        ]

    def __str__(self):
        name = getattr(self.customer, "display_name", str(self.customer))
        return (
            f"{name} - Rs. {self.requested_credit_limit:,.2f} "
            f"({self.get_status_display()})"
        )

    @property
    def change_amount(self):
        """Calculate the change in credit limit."""
        if self.previous_credit_limit is None:
            return self.requested_credit_limit
        return self.requested_credit_limit - self.previous_credit_limit

    def can_auto_approve(self):
        """Check if this request can be auto-approved."""
        from apps.credit.models.credit_settings import CreditSettings

        try:
            from django.db import connection
            tenant = connection.tenant
            settings = CreditSettings.objects.get_or_create_for_tenant(tenant)
            return self.requested_credit_limit <= settings.auto_approval_threshold
        except Exception:
            return False

    def approve(self, user, notes=""):
        """Approve this credit request."""
        self.status = ApprovalStatus.APPROVED
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.decision_notes = notes
        self.save()

        # Update the credit account if it exists
        if self.credit_account:
            self.credit_account.credit_limit = self.requested_credit_limit
            self.credit_account.available_credit = (
                self.requested_credit_limit
                - self.credit_account.outstanding_balance
            )
            self.credit_account.status = "active"
            self.credit_account.approved_by = user
            self.credit_account.approved_at = timezone.now()
            self.credit_account.save()

    def reject(self, user, notes=""):
        """Reject this credit request."""
        self.status = ApprovalStatus.REJECTED
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.decision_notes = notes
        self.save()

    def calculate_priority(self):
        """Auto-calculate priority based on amount and risk factors."""
        if self.requested_credit_limit >= Decimal("1000000"):
            self.priority = RequestPriority.URGENT
        elif self.requested_credit_limit >= Decimal("500000"):
            self.priority = RequestPriority.HIGH
        elif self.requested_credit_limit >= Decimal("100000"):
            self.priority = RequestPriority.MEDIUM
        else:
            self.priority = RequestPriority.LOW

        # Elevate priority based on credit account risk
        if self.credit_account:
            if self.credit_account.risk_score >= 70:
                self.priority = RequestPriority.URGENT
            elif self.credit_account.late_payment_count >= 2:
                if self.priority in (
                    RequestPriority.LOW,
                    RequestPriority.MEDIUM,
                ):
                    self.priority = RequestPriority.HIGH

        self.save(update_fields=["priority", "updated_on"])
        return self.priority

    def send_approval_notification(self):
        """Send notification upon approval (placeholder for notification system)."""
        import logging

        logger = logging.getLogger(__name__)
        logger.info(
            "Credit approval notification: %s approved for Rs. %s",
            self.customer,
            self.requested_credit_limit,
        )

    def send_rejection_notification(self):
        """Send notification upon rejection (placeholder for notification system)."""
        import logging

        logger = logging.getLogger(__name__)
        logger.info(
            "Credit rejection notification: %s rejected (reason: %s)",
            self.customer,
            self.decision_notes,
        )
