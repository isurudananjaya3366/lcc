"""PayrollProcessor service for calculating employee payroll."""

import logging
from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.utils import timezone

from apps.payroll.constants import ComponentType, LineType, PaymentStatus, PayrollStatus

logger = logging.getLogger(__name__)

# Standard working constants
STANDARD_WORKING_DAYS = Decimal("22")
STANDARD_WORKING_HOURS = Decimal("8")
OVERTIME_MULTIPLIER = Decimal("1.5")


class PayrollProcessor:
    """Processes payroll for employees in a payroll run.

    Handles eligibility checks, attendance integration, pro-rata calculations,
    earnings/deductions processing, statutory contributions, and batch processing.
    """

    def __init__(self, payroll_run):
        self.payroll_run = payroll_run
        self.period = payroll_run.payroll_period
        self.errors = []
        self._progress_callback = None

    # ── Entry Point ──────────────────────────────────────────

    @classmethod
    def process_period(cls, period_id, user=None):
        """Process payroll for a period by creating a run and processing it.

        Args:
            period_id: UUID of the PayrollPeriod.
            user: Optional user who initiated the processing.

        Returns:
            dict with processing results.
        """
        from apps.payroll.models import PayrollPeriod, PayrollRun

        period = PayrollPeriod.objects.get(pk=period_id)

        if not period.can_process():
            from django.core.exceptions import ValidationError
            raise ValidationError(
                f"Cannot process period: status is {period.status}, is_locked={period.is_locked}"
            )

        # Get next run number
        max_run = PayrollRun.objects.filter(
            payroll_period=period,
        ).order_by("-run_number").first()
        next_number = (max_run.run_number + 1) if max_run else 1

        run = PayrollRun.objects.create(
            payroll_period=period,
            run_number=next_number,
            status=PayrollStatus.DRAFT,
            processed_by=user,
        )

        processor = cls(run)
        return processor.process_batch()

    # ── Eligibility ──────────────────────────────────────────

    def get_eligible_employees(self):
        """Get employees eligible for payroll processing.

        Returns employees with active salary records who haven't been
        processed in this run yet. Filters for active employees within
        the period date range.
        """
        from apps.payroll.models import EmployeeSalary

        processed_employee_ids = self.payroll_run.employee_payrolls.values_list(
            "employee_id", flat=True
        )

        queryset = EmployeeSalary.objects.filter(
            is_current=True,
        ).exclude(
            employee_id__in=processed_employee_ids
        ).select_related("employee", "template")

        # Filter for active employees
        try:
            queryset = queryset.filter(employee__status="ACTIVE")
        except Exception:
            pass  # status field may not exist on Employee model

        # Filter by employment date range
        if self.period.start_date:
            try:
                queryset = queryset.filter(
                    employee__employment_date__lte=self.period.end_date,
                ).exclude(
                    employee__termination_date__lt=self.period.start_date,
                    employee__termination_date__isnull=False,
                )
            except Exception:
                pass  # employment_date / termination_date may not exist

        return queryset

    # ── Attendance ───────────────────────────────────────────

    def fetch_attendance_data(self, employee, start_date, end_date):
        """Fetch attendance data for an employee within the period.

        Returns a dict with attendance summary. Falls back to full
        working days if no attendance module data available.
        """
        total_working_days = self.calculate_working_days(start_date, end_date)

        # Default attendance (full working month)
        attendance = {
            "days_worked": total_working_days,
            "days_absent": 0,
            "unpaid_leave_days": 0,
            "overtime_hours": Decimal("0"),
            "late_count": 0,
            "total_working_days": total_working_days,
        }

        # Try to fetch from attendance module
        try:
            from apps.attendance.models import AttendanceRecord

            records = AttendanceRecord.objects.filter(
                employee=employee,
                date__gte=start_date,
                date__lte=end_date,
            )
            if records.exists():
                days_present = records.filter(status="PRESENT").count()
                days_absent = records.filter(status="ABSENT").count()
                overtime = records.aggregate(
                    total=models.Sum("overtime_hours")
                )["total"] or Decimal("0")
                late = records.filter(is_late=True).count()

                attendance.update({
                    "days_worked": days_present,
                    "days_absent": days_absent,
                    "overtime_hours": Decimal(str(overtime)),
                    "late_count": late,
                })
        except (ImportError, Exception):
            pass  # Attendance module not available, use defaults

        return attendance

    def calculate_working_days(self, start_date, end_date):
        """Calculate working days between two dates (excludes weekends)."""
        from datetime import timedelta

        working_days = 0
        current = start_date
        while current <= end_date:
            if current.weekday() < 5:
                working_days += 1
            current += timedelta(days=1)
        return working_days

    # ── Overtime ─────────────────────────────────────────────

    def calculate_overtime(self, basic_salary, overtime_hours):
        """Calculate overtime pay based on basic salary and hours."""
        if not overtime_hours or overtime_hours <= 0:
            return Decimal("0.00")

        overtime_hours = Decimal(str(overtime_hours))
        hourly_rate = basic_salary / STANDARD_WORKING_DAYS / STANDARD_WORKING_HOURS
        overtime_rate = hourly_rate * OVERTIME_MULTIPLIER
        return (overtime_hours * overtime_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    # ── Unpaid Leave ─────────────────────────────────────────

    def calculate_unpaid_leave_deduction(self, basic_salary, unpaid_days, total_working_days):
        """Calculate deduction for unpaid leave days."""
        if not unpaid_days or unpaid_days <= 0:
            return Decimal("0.00")

        total_working_days = Decimal(str(total_working_days)) if total_working_days else STANDARD_WORKING_DAYS
        per_day_salary = basic_salary / total_working_days
        return (Decimal(str(unpaid_days)) * per_day_salary).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    # ── Pro-Rata ─────────────────────────────────────────────

    def calculate_basic_pro_rata(self, basic_salary, days_worked, total_working_days):
        """Calculate pro-rated basic salary."""
        if not total_working_days or total_working_days <= 0:
            return basic_salary

        days_worked = Decimal(str(days_worked))
        total_working_days = Decimal(str(total_working_days))

        if days_worked >= total_working_days:
            return basic_salary

        pro_rata_factor = days_worked / total_working_days
        return (basic_salary * pro_rata_factor).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    # ── Earnings & Deductions ────────────────────────────────

    def calculate_earnings(self, employee_salary, attendance):
        """Process all earning components and return line items data.

        Returns a list of dicts representing PayrollLineItem data
        for each earning component.
        """
        from apps.payroll.models import EmployeeSalaryComponent

        line_items = []
        components = EmployeeSalaryComponent.objects.filter(
            employee_salary=employee_salary,
            component__component_type=ComponentType.EARNING,
        ).select_related("component")

        total_working_days = attendance.get("total_working_days", 22)
        days_worked = attendance.get("days_worked", total_working_days)

        for esc in components:
            comp = esc.component
            base_amount = esc.amount

            # Pro-rata for attendance-variable components
            if comp.is_attendance_based:
                final_amount = self.calculate_basic_pro_rata(
                    base_amount, days_worked, total_working_days
                )
                adjustment = final_amount - base_amount
            else:
                final_amount = base_amount
                adjustment = Decimal("0.00")

            line_items.append({
                "component": comp,
                "line_type": LineType.EARNING,
                "base_amount": base_amount,
                "calculated_amount": base_amount,
                "adjustment_amount": adjustment,
                "final_amount": final_amount,
                "description": comp.name,
                "calculation_notes": {
                    "is_attendance_based": comp.is_attendance_based,
                    "days_worked": days_worked,
                    "total_working_days": total_working_days,
                },
            })

        return line_items

    def calculate_deductions(self, employee_salary, gross_salary):
        """Process all deduction components and return line items data."""
        from apps.payroll.models import EmployeeSalaryComponent

        line_items = []
        components = EmployeeSalaryComponent.objects.filter(
            employee_salary=employee_salary,
            component__component_type=ComponentType.DEDUCTION,
        ).select_related("component")

        for esc in components:
            comp = esc.component
            base_amount = esc.amount

            line_items.append({
                "component": comp,
                "line_type": LineType.DEDUCTION,
                "base_amount": base_amount,
                "calculated_amount": base_amount,
                "adjustment_amount": Decimal("0.00"),
                "final_amount": base_amount,
                "description": comp.name,
                "calculation_notes": {},
            })

        return line_items

    # ── Gross & Net ──────────────────────────────────────────

    def calculate_gross(self, earning_line_items, overtime_amount):
        """Sum all earnings plus overtime to get gross salary."""
        total = sum(
            (item["final_amount"] for item in earning_line_items),
            Decimal("0.00"),
        )
        return total + overtime_amount

    def calculate_net(self, gross_salary, total_deductions):
        """Calculate net salary as gross minus deductions."""
        return gross_salary - total_deductions

    # ── Inline Statutory Calculations ────────────────────────

    def calculate_epf(self, basic_salary, employee_salary=None):
        """Calculate EPF contributions inline.

        Delegates to EPFCalculator if available, otherwise uses standard rates.
        """
        try:
            from apps.payroll.services.epf_calculator import EPFCalculator
            if employee_salary:
                return EPFCalculator.calculate(employee_salary)
        except (ImportError, Exception):
            pass
        employee_epf = (basic_salary * Decimal("0.08")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        employer_epf = (basic_salary * Decimal("0.12")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return {
            "epf_base": basic_salary,
            "employee_contribution": employee_epf,
            "employer_contribution": employer_epf,
            "employee_rate": Decimal("8.00"),
            "employer_rate": Decimal("12.00"),
        }

    def calculate_etf(self, basic_salary, employee_salary=None):
        """Calculate ETF contribution inline.

        Delegates to ETFCalculator if available, otherwise uses standard rate.
        """
        try:
            from apps.payroll.services.etf_calculator import ETFCalculator
            if employee_salary:
                return ETFCalculator.calculate(employee_salary)
        except (ImportError, Exception):
            pass
        employer_etf = (basic_salary * Decimal("0.03")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return {
            "etf_base": basic_salary,
            "employer_contribution": employer_etf,
        }

    def calculate_paye(self, gross_salary, employee_salary=None):
        """Calculate PAYE tax inline.

        Delegates to PAYECalculator if available, otherwise returns zero.
        """
        try:
            from apps.payroll.services.paye_calculator import PAYECalculator
            if employee_salary:
                return PAYECalculator.calculate(employee_salary)
        except (ImportError, Exception):
            pass
        return {
            "monthly_tax": Decimal("0.00"),
            "annual_projection": Decimal("0.00"),
            "annual_tax": Decimal("0.00"),
            "monthly_exemptions": Decimal("0.00"),
        }

    # ── Leave Integration ────────────────────────────────────

    def fetch_leave_data(self, employee, start_date, end_date):
        """Fetch unpaid leave days from the Leave module.

        Returns the number of unpaid leave days in the period.
        Falls back to 0 if the Leave module is not available.
        """
        try:
            from apps.leave.models import LeaveApplication
            unpaid_leaves = LeaveApplication.objects.filter(
                employee=employee,
                leave_type__is_paid=False,
                status="APPROVED",
                start_date__lte=end_date,
                end_date__gte=start_date,
            )
            total_unpaid = 0
            for leave in unpaid_leaves:
                overlap_start = max(leave.start_date, start_date)
                overlap_end = min(leave.end_date, end_date)
                total_unpaid += (overlap_end - overlap_start).days + 1
            return total_unpaid
        except (ImportError, Exception):
            return 0

    # ── Single Employee Processing ───────────────────────────

    def process_employee(self, employee_salary):
        """Process payroll for a single employee.

        Creates an EmployeePayroll record with all calculated amounts
        and associated PayrollLineItem records.
        """
        from apps.payroll.models import EmployeePayroll, PayrollLineItem

        employee = employee_salary.employee
        basic_salary = employee_salary.basic_salary

        # Fetch attendance
        attendance = self.fetch_attendance_data(
            employee, self.period.start_date, self.period.end_date
        )

        # Calculate earnings
        earning_items = self.calculate_earnings(employee_salary, attendance)

        # Calculate overtime
        overtime_amount = self.calculate_overtime(
            basic_salary, attendance.get("overtime_hours", 0)
        )

        # Calculate gross
        gross_salary = self.calculate_gross(earning_items, overtime_amount)

        # Calculate deductions from salary structure
        deduction_items = self.calculate_deductions(employee_salary, gross_salary)

        # Calculate statutory contributions
        from apps.payroll.models.epf_contribution import EPFContribution
        from apps.payroll.models.etf_contribution import ETFContribution
        from apps.payroll.models.paye_calculation import PAYECalculation
        from apps.payroll.services.epf_calculator import EPFCalculator
        from apps.payroll.services.etf_calculator import ETFCalculator
        from apps.payroll.services.paye_calculator import PAYECalculator

        epf_result = EPFCalculator.calculate(employee_salary)
        etf_result = ETFCalculator.calculate(employee_salary)
        paye_result = PAYECalculator.calculate(employee_salary)

        epf_employee = epf_result.get("employee_contribution", Decimal("0.00"))
        epf_employer = epf_result.get("employer_contribution", Decimal("0.00"))
        epf_base = epf_result.get("epf_base", Decimal("0.00"))
        etf_amount = etf_result.get("employer_contribution", Decimal("0.00"))
        etf_base = etf_result.get("etf_base", Decimal("0.00"))
        paye_tax = paye_result.get("monthly_tax", Decimal("0.00"))

        # Total deductions
        structure_deductions = sum(
            (item["final_amount"] for item in deduction_items),
            Decimal("0.00"),
        )
        total_deductions = structure_deductions + epf_employee + paye_tax

        # Net salary
        net_salary = self.calculate_net(gross_salary, total_deductions)

        # Create salary snapshot
        salary_snapshot = {
            "salary_id": str(employee_salary.pk),
            "basic_salary": str(basic_salary),
            "gross_salary": str(employee_salary.gross_salary),
            "effective_from": str(employee_salary.effective_from),
        }

        # Create EmployeePayroll record
        emp_payroll = EmployeePayroll.objects.create(
            payroll_run=self.payroll_run,
            employee=employee,
            employee_salary=employee_salary,
            salary_snapshot=salary_snapshot,
            days_worked=attendance["days_worked"],
            days_absent=attendance["days_absent"],
            unpaid_leave_days=attendance["unpaid_leave_days"],
            overtime_hours=attendance["overtime_hours"],
            late_count=attendance["late_count"],
            basic_salary=self.calculate_basic_pro_rata(
                basic_salary,
                attendance["days_worked"] + attendance["days_absent"],
                attendance["total_working_days"],
            ),
            overtime_amount=overtime_amount,
            gross_salary=gross_salary,
            total_deductions=total_deductions,
            net_salary=net_salary,
            epf_employee=epf_employee,
            epf_employer=epf_employer,
            etf=etf_amount,
            paye_tax=paye_tax,
            payment_status=PaymentStatus.PENDING,
        )

        # Create line items
        all_items = earning_items + deduction_items
        line_item_objects = [
            PayrollLineItem(
                employee_payroll=emp_payroll,
                component=item["component"],
                line_type=item["line_type"],
                base_amount=item["base_amount"],
                calculated_amount=item["calculated_amount"],
                adjustment_amount=item["adjustment_amount"],
                final_amount=item["final_amount"],
                description=item["description"],
                calculation_notes=item["calculation_notes"],
            )
            for item in all_items
        ]
        PayrollLineItem.objects.bulk_create(line_item_objects)

        # Create statutory contribution records
        calc_date = self.period.end_date

        epf_components = [
            item for item in earning_items
            if getattr(item["component"], "is_epf_applicable", False)
        ]
        base_details = {
            "components": [
                {"name": item["component"].name, "amount": str(item["final_amount"])}
                for item in epf_components
            ]
        }

        EPFContribution.objects.create(
            employee_payroll=emp_payroll,
            epf_base=epf_base,
            base_calculation_details=base_details,
            employee_amount=epf_employee,
            employer_amount=epf_employer,
            total_amount=epf_employee + epf_employer,
            employee_rate=epf_result.get("employee_rate", Decimal("8.00")) if "employee_rate" in epf_result else Decimal("8.00"),
            employer_rate=epf_result.get("employer_rate", Decimal("12.00")) if "employer_rate" in epf_result else Decimal("12.00"),
            calculation_date=calc_date,
        )

        ETFContribution.objects.create(
            employee_payroll=emp_payroll,
            etf_base=etf_base,
            base_calculation_details=base_details,
            employer_amount=etf_amount,
            calculation_date=calc_date,
        )

        PAYECalculation.objects.create(
            employee_payroll=emp_payroll,
            gross_income=gross_salary,
            taxable_income=Decimal(str(paye_result.get("annual_projection", Decimal("0.00")))),
            epf_deduction=epf_employee,
            exemptions={
                "monthly_exemptions": str(paye_result.get("monthly_exemptions", Decimal("0.00"))),
                "total_exemptions": str(paye_result.get("monthly_exemptions", Decimal("0.00")) * 12),
            },
            monthly_tax=paye_tax,
            annual_projected_tax=paye_result.get("annual_tax", Decimal("0.00")),
            calculation_date=calc_date,
        )

        return emp_payroll

    # ── Batch Processing ─────────────────────────────────────

    @transaction.atomic
    def process_batch(self, progress_callback=None):
        """Process payroll for all eligible employees.

        Updates the PayrollRun with totals and status.
        Optional progress_callback(current, total) for tracking.
        """
        from apps.payroll.models import PayrollRun

        # Mark run as processing
        self.payroll_run.status = PayrollStatus.PROCESSING
        self.payroll_run.started_at = timezone.now()
        self.payroll_run.save(update_fields=["status", "started_at", "updated_on"])

        eligible = self.get_eligible_employees()
        total = eligible.count()
        processed = 0
        errors = []

        totals = {
            "gross": Decimal("0.00"),
            "deductions": Decimal("0.00"),
            "net": Decimal("0.00"),
            "epf_employee": Decimal("0.00"),
            "epf_employer": Decimal("0.00"),
            "etf": Decimal("0.00"),
            "paye": Decimal("0.00"),
        }

        for es in eligible:
            try:
                emp_payroll = self.process_employee(es)
                processed += 1

                # Accumulate totals
                totals["gross"] += emp_payroll.gross_salary
                totals["deductions"] += emp_payroll.total_deductions
                totals["net"] += emp_payroll.net_salary
                totals["epf_employee"] += emp_payroll.epf_employee
                totals["epf_employer"] += emp_payroll.epf_employer
                totals["etf"] += emp_payroll.etf
                totals["paye"] += emp_payroll.paye_tax

                if progress_callback:
                    progress_callback(processed, total)

            except Exception as e:
                logger.exception(
                    "Error processing employee %s: %s", es.employee_id, str(e)
                )
                errors.append({
                    "employee_id": str(es.employee_id),
                    "error": str(e),
                    "timestamp": timezone.now().isoformat(),
                })

        # Update run with totals
        self.payroll_run.total_employees = processed
        self.payroll_run.total_gross = totals["gross"]
        self.payroll_run.total_deductions = totals["deductions"]
        self.payroll_run.total_net = totals["net"]
        self.payroll_run.total_epf_employee = totals["epf_employee"]
        self.payroll_run.total_epf_employer = totals["epf_employer"]
        self.payroll_run.total_etf = totals["etf"]
        self.payroll_run.total_paye = totals["paye"]
        self.payroll_run.error_count = len(errors)
        self.payroll_run.errors = errors
        self.payroll_run.completed_at = timezone.now()
        self.payroll_run.status = PayrollStatus.PROCESSED
        self.payroll_run.save()

        return {
            "processed": processed,
            "errors": len(errors),
            "total": total,
            "totals": {k: str(v) for k, v in totals.items()},
        }
