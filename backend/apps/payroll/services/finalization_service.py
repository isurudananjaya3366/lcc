"""PayrollFinalizationService for finalizing, bank file generation, and payment marking."""

import csv
import io
import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.payroll.constants import HistoryAction, PaymentStatus, PayrollStatus

logger = logging.getLogger(__name__)


class PayrollFinalizationService:
    """Handles finalization, bank file generation, and payment marking."""

    SUPPORTED_BANK_FORMATS = {
        "SLIPS": "Sri Lanka Interbank Payment System",
        "BOC": "Bank of Ceylon",
        "COMMERCIAL": "Commercial Bank Format",
        "CSV": "Generic CSV Format",
    }

    @transaction.atomic
    def finalize(self, run_id, finalized_by):
        """Finalize an approved payroll run, locking all data.

        Args:
            run_id: UUID of the PayrollRun.
            finalized_by: User finalizing the run.

        Returns:
            Finalized PayrollRun instance.
        """
        from apps.payroll.models import EmployeePayroll, PayrollRun
        from apps.payroll.models.payroll_history import PayrollHistory

        run = PayrollRun.objects.select_related("payroll_period").get(pk=run_id)

        if run.status != PayrollStatus.APPROVED:
            raise ValidationError(
                f"Cannot finalize: status is {run.status}, expected APPROVED."
            )

        previous_status = run.status

        # Lock the period
        period = run.payroll_period
        period.is_locked = True
        period.locked_at = timezone.now()
        period.locked_by = finalized_by
        period.save(update_fields=["is_locked", "locked_at", "locked_by", "updated_on"])

        # Lock individual employee payroll records
        EmployeePayroll.objects.filter(payroll_run=run).update(is_locked=True)

        # Update run status and tracking
        run.status = PayrollStatus.FINALIZED
        run.finalized_by = finalized_by
        run.finalized_at = timezone.now()
        run.save(update_fields=[
            "status", "finalized_by", "finalized_at", "updated_on",
        ])

        PayrollHistory.objects.create(
            payroll_run=run,
            action=HistoryAction.FINALIZED,
            previous_status=previous_status,
            new_status=run.status,
            performed_by=finalized_by,
            details={
                "period": str(period),
                "locked_period": True,
                "total_employees": run.total_employees,
            },
        )

        logger.info("Payroll run %s finalized by %s", run_id, finalized_by)
        self._send_notification(run, "finalized", finalized_by)
        return run

    def generate_bank_file(self, run_id, bank_code, generated_by):
        """Generate a bank transfer file for salary payments.

        Args:
            run_id: UUID of the PayrollRun.
            bank_code: Bank format code (SLIPS, BOC, COMMERCIAL, CSV).
            generated_by: User generating the file.

        Returns:
            dict with content, filename, and content_type.
        """
        from apps.payroll.models import EmployeePayroll, PayrollRun
        from apps.payroll.models.payroll_history import PayrollHistory

        if bank_code not in self.SUPPORTED_BANK_FORMATS:
            raise ValidationError(
                f"Unsupported bank format: {bank_code}. "
                f"Supported: {list(self.SUPPORTED_BANK_FORMATS.keys())}"
            )

        run = PayrollRun.objects.select_related("payroll_period").get(pk=run_id)

        if run.status != PayrollStatus.FINALIZED:
            raise ValidationError(
                f"Cannot generate bank file: status is {run.status}, expected FINALIZED."
            )

        employees = EmployeePayroll.objects.filter(
            payroll_run=run,
            payment_status=PaymentStatus.PENDING,
        ).select_related("employee").order_by("employee__first_name")

        period = run.payroll_period
        pay_date = period.pay_date
        records = []

        for emp_payroll in employees:
            emp = emp_payroll.employee
            bank_info = emp_payroll.bank_account or {}
            records.append({
                "account_no": bank_info.get("account_number", ""),
                "bank_code": bank_info.get("bank_code", ""),
                "branch_code": bank_info.get("branch_code", ""),
                "amount": emp_payroll.net_salary,
                "employee_name": f"{getattr(emp, 'first_name', '')} {getattr(emp, 'last_name', '')}".strip(),
                "reference": f"PAY-{period.period_year}{period.period_month:02d}-{run.run_number}",
            })

        if bank_code == "CSV":
            result = self._build_csv_bank_file(records, pay_date, period)
        elif bank_code == "SLIPS":
            result = self._build_slips_file(records, pay_date, period)
        elif bank_code in ("BOC", "COMMERCIAL"):
            result = self._build_bank_format_file(records, pay_date, period, bank_code)
        else:
            result = self._build_csv_bank_file(records, pay_date, period)

        PayrollHistory.objects.create(
            payroll_run=run,
            action=HistoryAction.BANK_FILE_GENERATED,
            previous_status=run.status,
            new_status=run.status,
            performed_by=generated_by,
            details={
                "bank_code": bank_code,
                "file_name": result["filename"],
                "total_amount": str(sum(r["amount"] for r in records)),
                "record_count": len(records),
            },
        )

        logger.info("Bank file generated for run %s, format=%s", run_id, bank_code)

        # Mark bank file as generated on the run
        run.bank_file_generated = True
        run.save(update_fields=["bank_file_generated", "updated_on"])

        return result

    def mark_as_paid(self, run_id, payment_reference, payment_date, marked_by):
        """Mark payroll as paid after bank transfer.

        Args:
            run_id: UUID of the PayrollRun.
            payment_reference: Bank transaction reference.
            payment_date: Actual payment date.
            marked_by: User marking as paid.

        Returns:
            Updated PayrollRun instance.
        """
        from apps.payroll.models import EmployeePayroll, PayrollRun
        from apps.payroll.models.payroll_history import PayrollHistory

        if not payment_reference:
            raise ValidationError("Payment reference is required.")

        run = PayrollRun.objects.get(pk=run_id)

        if run.status != PayrollStatus.FINALIZED:
            raise ValidationError(
                f"Cannot mark as paid: status is {run.status}, expected FINALIZED."
            )

        # Update all employee payroll records
        EmployeePayroll.objects.filter(
            payroll_run=run,
            payment_status=PaymentStatus.PENDING,
        ).update(
            payment_status=PaymentStatus.PAID,
            payment_reference=payment_reference,
            payment_date=payment_date,
        )

        # Update run payment tracking
        run.payment_reference = payment_reference
        run.payment_date = payment_date
        run.paid_at = timezone.now()
        run.save(update_fields=[
            "payment_reference", "payment_date", "paid_at", "updated_on",
        ])

        PayrollHistory.objects.create(
            payroll_run=run,
            action=HistoryAction.PAID,
            previous_status=run.status,
            new_status=run.status,
            performed_by=marked_by,
            details={
                "payment_reference": payment_reference,
                "payment_date": str(payment_date),
                "total_transferred": str(run.total_net),
            },
        )

        logger.info("Payroll run %s marked as paid, ref=%s", run_id, payment_reference)
        return run

    def get_finalization_status(self, run_id):
        """Get current finalization status and readiness."""
        from apps.payroll.models import PayrollRun

        run = PayrollRun.objects.select_related("payroll_period").get(pk=run_id)
        period = run.payroll_period

        bank_file_history = run.history.filter(
            action=HistoryAction.BANK_FILE_GENERATED,
        ).exists()

        paid_history = run.history.filter(
            action=HistoryAction.PAID,
        ).first()

        return {
            "is_finalized": run.status == PayrollStatus.FINALIZED,
            "is_locked": period.is_locked,
            "is_paid": paid_history is not None,
            "payment_reference": paid_history.details.get("payment_reference") if paid_history else None,
            "finalized_at": run.approved_at,
            "bank_file_available": bank_file_history,
        }

    def get_bank_file_formats(self):
        """Get list of supported bank file formats."""
        return dict(self.SUPPORTED_BANK_FORMATS)

    # ── Private helpers ──────────────────────────────────────

    def _build_csv_bank_file(self, records, pay_date, period):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Account No", "Bank Code", "Branch Code", "Amount", "Employee Name", "Reference"])
        for r in records:
            writer.writerow([
                r["account_no"], r["bank_code"], r["branch_code"],
                r["amount"], r["employee_name"], r["reference"],
            ])
        filename = f"PayrollBankFile_CSV_{period.period_year}{period.period_month:02d}.csv"
        return {"content": output.getvalue().encode("utf-8"), "filename": filename, "content_type": "text/csv"}

    def _build_slips_file(self, records, pay_date, period):
        lines = []
        total_amount = sum(r["amount"] for r in records)
        lines.append(f"HEADER|COMPANY|PAY|{pay_date}|{total_amount}|{len(records)}")
        for r in records:
            lines.append(
                f"DETAIL|{r['account_no']}|{r['bank_code']}|{r['branch_code']}"
                f"|{r['amount']}|{r['employee_name']}|{r['reference']}"
            )
        lines.append(f"FOOTER|{len(records)}|{total_amount}")
        content = "\n".join(lines)
        filename = f"PayrollBankFile_SLIPS_{period.period_year}{period.period_month:02d}.txt"
        return {"content": content.encode("utf-8"), "filename": filename, "content_type": "text/plain"}

    def _build_bank_format_file(self, records, pay_date, period, bank_code):
        lines = [
            "PAYROLL FILE",
            f"Date: {pay_date}",
            "",
        ]
        for i, r in enumerate(records, 1):
            lines.append(f"{i:03d}|{r['account_no']}|{r['employee_name']}|{r['amount']}")
        content = "\n".join(lines)
        filename = f"PayrollBankFile_{bank_code}_{period.period_year}{period.period_month:02d}.txt"
        return {"content": content.encode("utf-8"), "filename": filename, "content_type": "text/plain"}

    def _send_notification(self, run, action, performed_by):
        """Send notification email for finalization events.

        Stub implementation — logs the event. Full email integration
        can be connected to Django's send_mail or a notification service.
        """
        logger.info(
            "Notification: Payroll run %s %s by %s (period: %s)",
            run.pk, action, performed_by, run.payroll_period,
        )
