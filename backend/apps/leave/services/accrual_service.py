"""Leave accrual service for grant, monthly accrual, pro-rata, carry-forward, and expiry."""

import logging
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from django.utils import timezone

from apps.leave.models.leave_balance import LeaveBalance
from apps.leave.models.leave_policy import LeavePolicy

logger = logging.getLogger(__name__)

# Default carry-forward limit (days) and expiry (months after year end)
DEFAULT_MAX_CARRY_FORWARD = Decimal("7.00")
DEFAULT_CARRY_EXPIRY_MONTHS = 12


class LeaveAccrualService:
    """Handles all leave accrual calculations and year-end processing."""

    # ── Core Accrual Methods ─────────────────────────────────

    @staticmethod
    def grant_annual_accrual(employee, leave_type, year, grant_date=None):
        """Grant full annual entitlement at once (annual_grant method)."""
        entitlement = LeavePolicy.get_entitlement_days(employee, leave_type)
        if not entitlement:
            return {"success": False, "message": "No entitlement configured."}

        balance, created = LeaveAccrualService._get_or_create_balance(employee, leave_type, year)
        if not created and balance.opening_balance > Decimal("0.00"):
            return {"success": False, "message": "Annual grant already allocated for this year."}

        amount = Decimal(str(entitlement))
        balance.opening_balance = amount
        balance.allocated_days = Decimal("0.00")
        balance.last_accrual_date = grant_date or timezone.now().date()
        balance.save(update_fields=["opening_balance", "allocated_days", "last_accrual_date", "updated_on"])

        logger.info("Annual grant: %s %s days for %s year=%d", employee, amount, leave_type.name, year)
        return {
            "success": True,
            "balance": balance,
            "amount_accrued": amount,
            "new_available": balance.available_days,
            "message": f"Granted {amount} days.",
        }

    @staticmethod
    def process_monthly_accrual(employee, leave_type, year, month, accrual_date=None):
        """Credit leave monthly (annual entitlement / 12)."""
        entitlement = LeavePolicy.get_entitlement_days(employee, leave_type)
        if not entitlement:
            return {"success": False, "message": "No entitlement configured."}

        monthly_amount = (Decimal(str(entitlement)) / Decimal("12")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        balance, _created = LeaveAccrualService._get_or_create_balance(employee, leave_type, year)

        # Prevent double-accrual for same month
        accrual_dt = accrual_date or timezone.now().date()
        if balance.last_accrual_date and balance.last_accrual_date.month >= month and balance.last_accrual_date.year >= year:
            return {"success": False, "message": f"Accrual for month {month} already processed."}

        balance.allocated_days += monthly_amount
        balance.last_accrual_date = accrual_dt
        balance.save(update_fields=["allocated_days", "last_accrual_date", "updated_on"])

        logger.info("Monthly accrual: %s %s days month=%d for %s", employee, monthly_amount, month, leave_type.name)
        return {
            "success": True,
            "balance": balance,
            "amount_accrued": monthly_amount,
            "new_available": balance.available_days,
            "message": f"Accrued {monthly_amount} days for month {month}.",
        }

    @staticmethod
    def calculate_pro_rata(employee, leave_type, join_date, year, grant_immediately=True):
        """Calculate pro-rata entitlement for mid-year joiners."""
        entitlement = LeavePolicy.get_entitlement_days(employee, leave_type)
        if not entitlement:
            return {"success": False, "message": "No entitlement configured."}

        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        effective_start = max(join_date, year_start)

        if effective_start > year_end:
            return {"success": False, "message": "Join date is after the year end."}

        remaining_days = (year_end - effective_start).days + 1
        total_days_in_year = (year_end - year_start).days + 1
        pro_rata_amount = (
            Decimal(str(entitlement)) * Decimal(str(remaining_days)) / Decimal(str(total_days_in_year))
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if grant_immediately:
            balance, _created = LeaveAccrualService._get_or_create_balance(employee, leave_type, year)
            balance.allocated_days = pro_rata_amount
            balance.last_accrual_date = timezone.now().date()
            balance.save(update_fields=["allocated_days", "last_accrual_date", "updated_on"])
            return {
                "success": True,
                "balance": balance,
                "amount_accrued": pro_rata_amount,
                "new_available": balance.available_days,
                "message": f"Pro-rata: {pro_rata_amount} days ({remaining_days}/{total_days_in_year} of year).",
            }

        return {
            "success": True,
            "balance": None,
            "amount_accrued": pro_rata_amount,
            "new_available": None,
            "message": f"Pro-rata calculated: {pro_rata_amount} days (not yet granted).",
        }

    # ── Carry Forward & Expiry ───────────────────────────────

    @staticmethod
    def process_carry_forward(employee, leave_type, from_year, to_year):
        """Carry unused days from one year to the next, respecting limits."""
        try:
            from_balance = LeaveBalance.objects.get(employee=employee, leave_type=leave_type, year=from_year)
        except LeaveBalance.DoesNotExist:
            return {"success": False, "message": f"No balance found for year {from_year}."}

        unused = from_balance.available_days
        if unused <= Decimal("0.00"):
            return {"success": True, "message": "No unused days to carry forward.", "amount_accrued": Decimal("0.00")}

        to_carry, forfeited = LeaveAccrualService._calculate_carry_forward_limit(leave_type, unused)

        to_balance, _created = LeaveAccrualService._get_or_create_balance(employee, leave_type, to_year)
        to_balance.carried_from_previous = to_carry
        to_balance.carry_forward_expiry = date(to_year, 12, 31)
        to_balance.save(update_fields=["carried_from_previous", "carry_forward_expiry", "updated_on"])

        logger.info(
            "Carry forward: %s %s days (forfeited %s) %s %d→%d",
            employee, to_carry, forfeited, leave_type.name, from_year, to_year,
        )
        return {
            "success": True,
            "balance": to_balance,
            "amount_accrued": to_carry,
            "forfeited": forfeited,
            "new_available": to_balance.available_days,
            "message": f"Carried {to_carry} days, forfeited {forfeited} days.",
        }

    @staticmethod
    def check_and_expire_leaves(date_check=None):
        """Expire carried-forward days past their expiry date."""
        check_date = date_check or timezone.now().date()
        expired_balances = LeaveBalance.objects.filter(
            carry_forward_expiry__lt=check_date,
            carried_from_previous__gt=Decimal("0.00"),
            is_active=True,
        )

        results = []
        for balance in expired_balances:
            result = LeaveAccrualService.expire_carried_leave(balance)
            results.append(result)

        return {
            "success": True,
            "expired_count": len(results),
            "details": results,
        }

    @staticmethod
    def expire_carried_leave(balance):
        """Zero out carried_from_previous on a single expired balance."""
        expired_amount = balance.carried_from_previous
        balance.carried_from_previous = Decimal("0.00")
        balance.save(update_fields=["carried_from_previous", "updated_on"])

        logger.info("Expired carry-forward: %s %s days for %s", balance.employee, expired_amount, balance.leave_type.name)
        return {
            "employee": str(balance.employee),
            "leave_type": balance.leave_type.name,
            "expired_days": expired_amount,
        }

    @staticmethod
    def execute_year_end_rollover(from_year, to_year):
        """Orchestrate full year-end: carry forward + new allocations."""
        from apps.leave.models import LeaveType

        active_balances = LeaveBalance.objects.filter(year=from_year, is_active=True).select_related(
            "employee", "leave_type"
        )

        carry_success = 0
        carry_failed = 0
        alloc_success = 0
        alloc_failed = 0

        processed_employees = set()

        for balance in active_balances:
            # Carry forward
            result = LeaveAccrualService.process_carry_forward(
                balance.employee, balance.leave_type, from_year, to_year
            )
            if result["success"]:
                carry_success += 1
            else:
                carry_failed += 1

            # Grant new year allocation
            alloc_result = LeaveAccrualService.grant_annual_accrual(
                balance.employee, balance.leave_type, to_year
            )
            if alloc_result["success"]:
                alloc_success += 1
            else:
                alloc_failed += 1

            processed_employees.add(str(balance.employee_id))

        return {
            "success": True,
            "total_employees": len(processed_employees),
            "total_leave_types": active_balances.count(),
            "carry_forward_success": carry_success,
            "carry_forward_failed": carry_failed,
            "new_allocation_success": alloc_success,
            "new_allocation_failed": alloc_failed,
        }

    # ── Helpers ──────────────────────────────────────────────

    @staticmethod
    def _get_or_create_balance(employee, leave_type, year):
        return LeaveBalance.objects.get_or_create(
            employee=employee,
            leave_type=leave_type,
            year=year,
            defaults={"is_active": True},
        )

    @staticmethod
    def _calculate_carry_forward_limit(leave_type, unused_days):
        """Return (to_carry, forfeited) tuple respecting max carry-forward."""
        max_carry = DEFAULT_MAX_CARRY_FORWARD
        to_carry = min(unused_days, max_carry)
        forfeited = unused_days - to_carry
        return to_carry, forfeited

    # ── Validation ───────────────────────────────────────────

    @staticmethod
    def validate_accrual_eligibility(employee, leave_type, date_check=None):
        """Check if employee is eligible for accrual."""
        check_date = date_check or timezone.now().date()

        if not leave_type.is_active:
            return False, "Leave type is inactive."

        if leave_type.min_service_months > 0 and hasattr(employee, "date_of_joining"):
            join_date = employee.date_of_joining
            if join_date:
                months_served = (check_date.year - join_date.year) * 12 + (check_date.month - join_date.month)
                if months_served < leave_type.min_service_months:
                    return False, f"Requires {leave_type.min_service_months} months service ({months_served} served)."

        return True, "Eligible."
