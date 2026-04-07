"""Leave Request Service for the Leave Management app.

Handles leave request lifecycle: creation, submission, approval,
rejection, cancellation, and recall with proper status transitions.
"""

import logging
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.leave.constants import LeaveRequestStatus
from apps.leave.models.leave_balance import LeaveBalance
from apps.leave.models.leave_request import LeaveRequest

logger = logging.getLogger(__name__)


class LeaveRequestService:
    """Service class managing leave request operations and workflows."""

    # ── Valid Status Transitions ─────────────────────────────
    VALID_TRANSITIONS = {
        LeaveRequestStatus.DRAFT: [LeaveRequestStatus.PENDING],
        LeaveRequestStatus.PENDING: [
            LeaveRequestStatus.APPROVED,
            LeaveRequestStatus.REJECTED,
            LeaveRequestStatus.CANCELLED,
        ],
        LeaveRequestStatus.APPROVED: [LeaveRequestStatus.RECALLED],
    }

    # ── Create & Submit ──────────────────────────────────────

    @classmethod
    def create_draft(cls, employee, leave_type_id, data):
        """Create a new leave request in DRAFT status.

        Args:
            employee: Employee model instance.
            leave_type_id: UUID of the leave type.
            data: dict with start_date, end_date, reason, etc.

        Returns:
            LeaveRequest instance.
        """
        leave_request = LeaveRequest(
            employee=employee,
            leave_type_id=leave_type_id,
            start_date=data["start_date"],
            end_date=data["end_date"],
            total_days=data.get("total_days", cls._calculate_days(data)),
            is_half_day=data.get("is_half_day", False),
            half_day_type=data.get("half_day_type"),
            reason=data.get("reason", ""),
            contact_during_leave=data.get("contact_during_leave", ""),
            status=LeaveRequestStatus.DRAFT,
        )
        leave_request.full_clean()
        leave_request.save()

        logger.info(
            "Leave request draft created: %s for employee %s",
            leave_request.id,
            employee.id,
        )
        return leave_request

    @classmethod
    @transaction.atomic
    def submit(cls, request_id, user=None):
        """Submit a draft leave request for approval.

        Transitions: DRAFT → PENDING
        Validates balance and overlap before submission.

        Args:
            request_id: UUID of the leave request.
            user: Optional user performing the action.

        Returns:
            Updated LeaveRequest instance.

        Raises:
            ValueError: If transition is invalid or validation fails.
        """
        leave_request = LeaveRequest.objects.select_for_update().get(id=request_id)
        cls._validate_transition(leave_request, LeaveRequestStatus.PENDING)

        cls.validate_balance(leave_request)
        cls.check_overlap(leave_request)

        leave_request.status = LeaveRequestStatus.PENDING
        leave_request.submitted_at = timezone.now()
        leave_request.save(update_fields=["status", "submitted_at", "updated_on"])

        # Update pending balance
        cls._update_pending_balance(leave_request, add=True)

        logger.info("Leave request submitted: %s", leave_request.id)
        return leave_request

    # ── Validation ───────────────────────────────────────────

    @classmethod
    def validate_balance(cls, leave_request):
        """Validate that the employee has sufficient leave balance.

        Args:
            leave_request: LeaveRequest instance.

        Raises:
            ValueError: If insufficient balance.
        """
        year = leave_request.start_date.year
        try:
            balance = LeaveBalance.objects.get(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                year=year,
                is_active=True,
            )
        except LeaveBalance.DoesNotExist:
            raise ValueError(
                f"No active leave balance found for {leave_request.leave_type.name} "
                f"in year {year}."
            )

        if not balance.has_sufficient_balance(leave_request.total_days):
            raise ValueError(
                f"Insufficient leave balance. Available: {balance.available_days}, "
                f"Requested: {leave_request.total_days}."
            )

    @classmethod
    def check_overlap(cls, leave_request):
        """Check for overlapping leave requests.

        Args:
            leave_request: LeaveRequest instance.

        Raises:
            ValueError: If overlapping active request exists.
        """
        overlapping = LeaveRequest.objects.filter(
            employee=leave_request.employee,
            start_date__lte=leave_request.end_date,
            end_date__gte=leave_request.start_date,
            status__in=[
                LeaveRequestStatus.PENDING,
                LeaveRequestStatus.APPROVED,
            ],
            is_deleted=False,
        ).exclude(id=leave_request.id)

        if overlapping.exists():
            raise ValueError(
                "Overlapping leave request exists for the selected date range."
            )

    # ── Approval Workflow ────────────────────────────────────

    @classmethod
    @transaction.atomic
    def approve(cls, request_id, approved_by, notes=""):
        """Approve a pending leave request.

        Transitions: PENDING → APPROVED
        Deducts from pending and adds to used balance.

        Args:
            request_id: UUID of the leave request.
            approved_by: User who approves (PlatformUser).
            notes: Optional approval notes.

        Returns:
            Updated LeaveRequest instance.

        Raises:
            ValueError: If transition is invalid.
        """
        leave_request = LeaveRequest.objects.select_for_update().get(id=request_id)
        cls._validate_transition(leave_request, LeaveRequestStatus.APPROVED)

        leave_request.status = LeaveRequestStatus.APPROVED
        leave_request.approved_by = approved_by
        leave_request.approved_at = timezone.now()
        leave_request.save(
            update_fields=[
                "status",
                "approved_by",
                "approved_at",
                "updated_on",
            ]
        )

        # Move from pending to used balance
        cls._update_pending_balance(leave_request, add=False)
        cls._update_used_balance(leave_request, add=True)

        logger.info(
            "Leave request approved: %s by %s",
            leave_request.id,
            approved_by,
        )
        return leave_request

    @classmethod
    @transaction.atomic
    def reject(cls, request_id, rejected_by, reason=""):
        """Reject a pending leave request.

        Transitions: PENDING → REJECTED

        Args:
            request_id: UUID of the leave request.
            rejected_by: User who rejects.
            reason: Rejection reason.

        Returns:
            Updated LeaveRequest instance.

        Raises:
            ValueError: If transition is invalid.
        """
        leave_request = LeaveRequest.objects.select_for_update().get(id=request_id)
        cls._validate_transition(leave_request, LeaveRequestStatus.REJECTED)

        leave_request.status = LeaveRequestStatus.REJECTED
        leave_request.rejection_reason = reason
        leave_request.save(
            update_fields=["status", "rejection_reason", "updated_on"]
        )

        # Release pending balance
        cls._update_pending_balance(leave_request, add=False)

        logger.info("Leave request rejected: %s", leave_request.id)
        return leave_request

    @classmethod
    @transaction.atomic
    def cancel(cls, request_id, user=None):
        """Cancel a pending leave request.

        Transitions: PENDING → CANCELLED

        Args:
            request_id: UUID of the leave request.
            user: User requesting cancellation.

        Returns:
            Updated LeaveRequest instance.

        Raises:
            ValueError: If transition is invalid.
        """
        leave_request = LeaveRequest.objects.select_for_update().get(id=request_id)
        cls._validate_transition(leave_request, LeaveRequestStatus.CANCELLED)

        leave_request.status = LeaveRequestStatus.CANCELLED
        leave_request.save(update_fields=["status", "updated_on"])

        # Release pending balance
        cls._update_pending_balance(leave_request, add=False)

        logger.info("Leave request cancelled: %s", leave_request.id)
        return leave_request

    @classmethod
    @transaction.atomic
    def recall(cls, request_id, user, reason=""):
        """Recall an approved leave request.

        Transitions: APPROVED → RECALLED
        Reverses the used balance deduction.

        Args:
            request_id: UUID of the leave request.
            user: User requesting recall.
            reason: Recall reason.

        Returns:
            Updated LeaveRequest instance.

        Raises:
            ValueError: If transition is invalid.
        """
        leave_request = LeaveRequest.objects.select_for_update().get(id=request_id)
        cls._validate_transition(leave_request, LeaveRequestStatus.RECALLED)

        leave_request.status = LeaveRequestStatus.RECALLED
        leave_request.recalled_at = timezone.now()
        leave_request.recalled_reason = reason
        leave_request.save(
            update_fields=[
                "status",
                "recalled_at",
                "recalled_reason",
                "updated_on",
            ]
        )

        # Reverse used balance
        cls._update_used_balance(leave_request, add=False)

        logger.info("Leave request recalled: %s", leave_request.id)
        return leave_request

    # ── Query Methods ────────────────────────────────────────

    @classmethod
    def get_request(cls, request_id):
        """Retrieve a single leave request by ID."""
        return LeaveRequest.objects.select_related(
            "employee", "leave_type", "approved_by"
        ).get(id=request_id)

    @classmethod
    def get_employee_requests(cls, employee_id, year=None, status=None):
        """Get leave requests for an employee with optional filters.

        Args:
            employee_id: UUID of the employee.
            year: Optional year filter.
            status: Optional status filter.

        Returns:
            QuerySet of LeaveRequest.
        """
        qs = LeaveRequest.objects.filter(
            employee_id=employee_id,
            is_deleted=False,
        ).select_related("leave_type")

        if year:
            qs = qs.filter(start_date__year=year)
        if status:
            qs = qs.filter(status=status)

        return qs

    @classmethod
    def get_pending_for_manager(cls, manager_employee_ids=None):
        """Get pending leave requests, optionally filtered by direct reports.

        Args:
            manager_employee_ids: Optional list of employee IDs
                (direct reports of the manager).

        Returns:
            QuerySet of pending LeaveRequest.
        """
        qs = LeaveRequest.objects.filter(
            status=LeaveRequestStatus.PENDING,
            is_deleted=False,
        ).select_related("employee", "leave_type")

        if manager_employee_ids is not None:
            qs = qs.filter(employee_id__in=manager_employee_ids)

        return qs

    # ── Private Helpers ──────────────────────────────────────

    @classmethod
    def _validate_transition(cls, leave_request, target_status):
        """Validate that the status transition is allowed.

        Raises:
            ValueError: If transition is not valid.
        """
        allowed = cls.VALID_TRANSITIONS.get(leave_request.status, [])
        if target_status not in allowed:
            raise ValueError(
                f"Cannot transition from {leave_request.status} to {target_status}."
            )

    @classmethod
    def _calculate_days(cls, data):
        """Calculate total leave days from date range.

        Simple calculation: end_date - start_date + 1.
        Half-day returns 0.5.
        """
        if data.get("is_half_day"):
            return Decimal("0.5")

        start = data["start_date"]
        end = data["end_date"]
        if isinstance(start, date) and isinstance(end, date):
            return Decimal(str((end - start).days + 1))
        return Decimal("1")

    @classmethod
    def _update_pending_balance(cls, leave_request, add=True):
        """Update pending_days on the leave balance.

        Args:
            leave_request: LeaveRequest instance.
            add: If True, add to pending. If False, subtract.
        """
        year = leave_request.start_date.year
        try:
            balance = LeaveBalance.objects.get(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                year=year,
                is_active=True,
            )
            if add:
                balance.pending_days += leave_request.total_days
            else:
                balance.pending_days = max(
                    Decimal("0"),
                    balance.pending_days - leave_request.total_days,
                )
            balance.save(update_fields=["pending_days", "updated_on"])
        except LeaveBalance.DoesNotExist:
            logger.warning(
                "No balance found for employee %s, leave type %s, year %s",
                leave_request.employee_id,
                leave_request.leave_type_id,
                year,
            )

    @classmethod
    def _update_used_balance(cls, leave_request, add=True):
        """Update used_days on the leave balance.

        Args:
            leave_request: LeaveRequest instance.
            add: If True, add to used. If False, subtract (for recall).
        """
        year = leave_request.start_date.year
        try:
            balance = LeaveBalance.objects.get(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                year=year,
                is_active=True,
            )
            if add:
                balance.used_days += leave_request.total_days
            else:
                balance.used_days = max(
                    Decimal("0"),
                    balance.used_days - leave_request.total_days,
                )
            balance.save(update_fields=["used_days", "updated_on"])
        except LeaveBalance.DoesNotExist:
            logger.warning(
                "No balance found for employee %s, leave type %s, year %s",
                leave_request.employee_id,
                leave_request.leave_type_id,
                year,
            )
