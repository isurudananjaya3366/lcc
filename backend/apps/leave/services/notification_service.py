"""Leave Notification Service for the Leave Management app.

Handles email notifications for leave request lifecycle events:
submission, approval, rejection, cancellation, reminders, and expiry.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from apps.leave.constants import LeaveRequestStatus

logger = logging.getLogger(__name__)


class LeaveNotificationService:
    """Service class for leave-related email notifications."""

    def __init__(self, tenant=None):
        self.tenant = tenant

    # ── Core Notification Methods ────────────────────────────

    def notify_request_submitted(self, leave_request):
        """Notify manager/approver about a new leave request.

        Args:
            leave_request: Submitted LeaveRequest instance.

        Returns:
            bool: True if notification sent successfully.
        """
        approver = self._get_approver(leave_request)
        if not approver:
            logger.warning(
                "No approver found for leave request %s", leave_request.id
            )
            return False

        recipient_email = self._get_email(approver)
        if not recipient_email:
            return False

        urgency = self._determine_urgency(leave_request)
        subject = self._generate_subject_line(leave_request, urgency)

        context = {
            "employee": self._format_employee_data(leave_request.employee),
            "leave_request": self._format_leave_request_data(leave_request),
            "urgency": urgency,
        }

        return self._send_notification(
            recipient_email, subject,
            "leave/emails/request_submitted.html", context,
        )

    def notify_approval(self, leave_request):
        """Notify employee that their leave request was approved.

        Args:
            leave_request: Approved LeaveRequest instance.

        Returns:
            bool: True if notification sent successfully.
        """
        recipient_email = self._get_email(leave_request.employee)
        if not recipient_email:
            return False

        subject = f"Leave Request Approved: {leave_request.leave_type.name}"
        context = {
            "employee": self._format_employee_data(leave_request.employee),
            "leave_request": self._format_leave_request_data(leave_request),
            "approver": str(leave_request.approved_by) if leave_request.approved_by else "",
            "approved_at": (
                leave_request.approved_at.isoformat()
                if leave_request.approved_at
                else ""
            ),
        }

        return self._send_notification(
            recipient_email, subject,
            "leave/emails/approval.html", context,
        )

    def notify_rejection(self, leave_request):
        """Notify employee that their leave request was rejected.

        Args:
            leave_request: Rejected LeaveRequest instance.

        Returns:
            bool: True if notification sent successfully.
        """
        recipient_email = self._get_email(leave_request.employee)
        if not recipient_email:
            return False

        subject = f"Leave Request Rejected: {leave_request.leave_type.name}"
        context = {
            "employee": self._format_employee_data(leave_request.employee),
            "leave_request": self._format_leave_request_data(leave_request),
            "rejection_reason": leave_request.rejection_reason,
        }

        return self._send_notification(
            recipient_email, subject,
            "leave/emails/rejection.html", context,
        )

    def notify_cancellation(self, leave_request):
        """Notify both parties about leave cancellation.

        Args:
            leave_request: Cancelled LeaveRequest instance.

        Returns:
            bool: True if at least one notification sent.
        """
        # Notify employee
        emp_email = self._get_email(leave_request.employee)
        subject = f"Leave Request Cancelled: {leave_request.leave_type.name}"
        context = {
            "employee": self._format_employee_data(leave_request.employee),
            "leave_request": self._format_leave_request_data(leave_request),
        }

        emp_sent = False
        if emp_email:
            emp_sent = self._send_notification(
                emp_email, subject,
                "leave/emails/cancellation.html", context,
            )

        # Notify approver/manager
        approver = self._get_approver(leave_request)
        mgr_sent = False
        if approver:
            mgr_email = self._get_email(approver)
            if mgr_email:
                mgr_sent = self._send_notification(
                    mgr_email, subject,
                    "leave/emails/cancellation.html", context,
                )

        return emp_sent or mgr_sent

    def notify_upcoming_leave(self, leave_request, days_before=3):
        """Send reminder for upcoming approved leave.

        Args:
            leave_request: Approved LeaveRequest instance.
            days_before: Days before leave starts.

        Returns:
            bool: True if notification sent.
        """
        recipient_email = self._get_email(leave_request.employee)
        if not recipient_email:
            return False

        subject = (
            f"Reminder: {leave_request.leave_type.name} starts in "
            f"{days_before} day(s)"
        )
        context = {
            "employee": self._format_employee_data(leave_request.employee),
            "leave_request": self._format_leave_request_data(leave_request),
            "days_before": days_before,
        }

        return self._send_notification(
            recipient_email, subject,
            "leave/emails/upcoming_leave.html", context,
        )

    def notify_expiring_balance(self, leave_balance, days_until_expiry):
        """Notify employee about expiring leave balance.

        Args:
            leave_balance: LeaveBalance instance with expiring carry-forward.
            days_until_expiry: Days until expiry.

        Returns:
            bool: True if notification sent.
        """
        recipient_email = self._get_email(leave_balance.employee)
        if not recipient_email:
            return False

        subject = (
            f"Leave Balance Expiring: {leave_balance.leave_type.name} "
            f"in {days_until_expiry} days"
        )
        context = {
            "employee": self._format_employee_data(leave_balance.employee),
            "leave_type": leave_balance.leave_type.name,
            "available_days": str(leave_balance.available_days),
            "expiry_date": (
                leave_balance.carry_forward_expiry.isoformat()
                if leave_balance.carry_forward_expiry
                else ""
            ),
            "days_until_expiry": days_until_expiry,
        }

        return self._send_notification(
            recipient_email, subject,
            "leave/emails/expiring_balance.html", context,
        )

    def notify_balance_allocated(self, employee, year):
        """Notify employee about new year leave allocation.

        Args:
            employee: Employee instance.
            year: Allocation year.

        Returns:
            bool: True if notification sent.
        """
        recipient_email = self._get_email(employee)
        if not recipient_email:
            return False

        subject = f"Leave Balance Allocated for {year}"
        context = {
            "employee": self._format_employee_data(employee),
            "year": year,
        }

        return self._send_notification(
            recipient_email, subject,
            "leave/emails/balance_allocated.html", context,
        )

    # ── Batch Methods ────────────────────────────────────────

    def send_bulk_expiry_notifications(self, targets):
        """Send expiry notifications to multiple employees.

        Args:
            targets: List of (leave_balance, days_until_expiry) tuples.

        Returns:
            Dict with success and failed counts.
        """
        success = 0
        failed = 0
        for balance, days in targets:
            if self.notify_expiring_balance(balance, days):
                success += 1
            else:
                failed += 1
        return {"success": success, "failed": failed}

    def send_bulk_upcoming_reminders(self, targets):
        """Send upcoming leave reminders to multiple employees.

        Args:
            targets: List of (leave_request, days_before) tuples.

        Returns:
            Dict with success and failed counts.
        """
        success = 0
        failed = 0
        for lr, days in targets:
            if self.notify_upcoming_leave(lr, days):
                success += 1
            else:
                failed += 1
        return {"success": success, "failed": failed}

    # ── Private Helpers ──────────────────────────────────────

    def _send_notification(self, recipient_email, subject, template, context):
        """Send email notification using Django's email framework.

        Returns:
            bool: True if sent successfully.
        """
        try:
            # Try to render template; fall back to plain text
            try:
                html_content = render_to_string(template, context)
            except Exception:
                html_content = None

            plain_text = f"{subject}\n\n{str(context)}"

            send_mail(
                subject=subject,
                message=plain_text,
                from_email=getattr(
                    settings, "DEFAULT_FROM_EMAIL", "noreply@lankacommerce.com"
                ),
                recipient_list=[recipient_email],
                html_message=html_content,
                fail_silently=True,
            )
            logger.info("Notification sent to %s: %s", recipient_email, subject)
            return True
        except Exception as e:
            logger.error(
                "Failed to send notification to %s: %s",
                recipient_email,
                str(e),
            )
            return False

    @staticmethod
    def _get_approver(leave_request):
        """Get the approver for a leave request.

        Fallback chain: approved_by → employee.reporting_manager
        """
        if leave_request.approved_by:
            return leave_request.approved_by

        employee = leave_request.employee
        manager = getattr(employee, "reporting_manager", None)
        return manager

    @staticmethod
    def _get_email(user_or_employee):
        """Extract email from user or employee."""
        if hasattr(user_or_employee, "email") and user_or_employee.email:
            return user_or_employee.email
        user = getattr(user_or_employee, "user", None)
        if user and hasattr(user, "email"):
            return user.email
        return None

    def _determine_urgency(self, leave_request):
        """Determine urgency of a leave request."""
        today = timezone.now().date()
        days_until_start = (leave_request.start_date - today).days

        if days_until_start < 0:
            return {
                "is_urgent": True,
                "days_until_start": days_until_start,
                "message": "RETROACTIVE — leave start date has passed.",
            }
        if days_until_start == 0:
            return {
                "is_urgent": True,
                "days_until_start": 0,
                "message": "Leave starts TODAY.",
            }
        if days_until_start <= 3:
            return {
                "is_urgent": True,
                "days_until_start": days_until_start,
                "message": f"URGENT — leave starts in {days_until_start} day(s).",
            }
        return {
            "is_urgent": False,
            "days_until_start": days_until_start,
            "message": f"Leave starts in {days_until_start} days.",
        }

    def _generate_subject_line(self, leave_request, urgency_info):
        """Generate email subject line with urgency prefix."""
        emp_name = self._format_employee_data(leave_request.employee).get(
            "name", "Employee"
        )
        base = f"New Leave Request from {emp_name}"
        if urgency_info.get("is_urgent"):
            return f"URGENT: {base}"
        return base

    @staticmethod
    def _format_employee_data(employee):
        """Format employee data for template context."""
        user = getattr(employee, "user", None)
        name = ""
        if user:
            first = getattr(user, "first_name", "")
            last = getattr(user, "last_name", "")
            name = f"{first} {last}".strip() or str(user.email)

        return {
            "id": str(employee.id),
            "name": name,
            "department": (
                str(employee.department.name)
                if hasattr(employee, "department") and employee.department
                else ""
            ),
        }

    @staticmethod
    def _format_leave_request_data(leave_request):
        """Format leave request data for template context."""
        return {
            "id": str(leave_request.id),
            "leave_type": leave_request.leave_type.name,
            "start_date": leave_request.start_date.isoformat(),
            "end_date": leave_request.end_date.isoformat(),
            "total_days": str(leave_request.total_days),
            "status": leave_request.status,
            "reason": leave_request.reason,
            "is_half_day": leave_request.is_half_day,
        }
