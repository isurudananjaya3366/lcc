"""Employee model for the Employees application."""

from datetime import date, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin
from apps.employees.constants import (
    DEFAULT_EMPLOYEE_STATUS,
    DEFAULT_EMPLOYMENT_TYPE,
    EMPLOYEE_STATUS_ACTIVE,
    EMPLOYEE_STATUS_CHOICES,
    EMPLOYEE_STATUS_INACTIVE,
    EMPLOYEE_STATUS_ON_LEAVE,
    EMPLOYEE_STATUS_RESIGNED,
    EMPLOYEE_STATUS_TERMINATED,
    EMPLOYMENT_TYPE_CHOICES,
    GENDER_CHOICES,
    GENDER_FEMALE,
    GENDER_MALE,
    MARITAL_STATUS_CHOICES,
    MARITAL_STATUS_MARRIED,
    RETIREMENT_AGE,
    TERMINATION_REASON_CHOICES,
    WORK_LOCATION_TYPE_CHOICES,
)
from apps.employees.validators.nic_validator import (
    extract_birth_year_from_nic,
    extract_gender_from_nic,
    validate_nic,
)


def employee_photo_path(instance, filename):
    """Generate upload path for employee profile photos."""
    return f"employees/photos/{instance.employee_id}/{filename}"


class Employee(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Comprehensive employee record within a tenant organisation.

    Stores personal information, employment details, and links to
    user accounts. Employee ID is auto-generated in EMP-XXXX format.
    """

    # ── Employee ID ─────────────────────────────────────────────────
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        blank=True,
        verbose_name="Employee ID",
        help_text="Auto-generated employee identifier (EMP-0001 format).",
    )

    # ── User Link (Optional) ───────────────────────────────────────
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee",
        verbose_name="User Account",
        help_text="Optional link to a user account for system access.",
    )

    # ── Name Fields ─────────────────────────────────────────────────
    first_name = models.CharField(
        max_length=100,
        verbose_name="First Name",
        help_text="Employee's given name.",
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name="Last Name",
        help_text="Employee's family name.",
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Middle Name",
        help_text="Employee's middle name or initial.",
    )
    preferred_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Preferred Name",
        help_text="Nickname or preferred name for informal use.",
    )

    # ── Profile Photo ───────────────────────────────────────────────
    profile_photo = models.ImageField(
        upload_to=employee_photo_path,
        blank=True,
        null=True,
        verbose_name="Profile Photo",
        help_text="Employee's profile photograph.",
    )

    # ── NIC (National Identity Card) ────────────────────────────────
    nic_number = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
        validators=[validate_nic],
        verbose_name="NIC Number",
        help_text="Sri Lanka NIC number (old: 912345678V, new: 199112345678).",
    )

    # ── Date of Birth ───────────────────────────────────────────────
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date of Birth",
        help_text="Employee's date of birth.",
    )

    # ── Gender ──────────────────────────────────────────────────────
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True,
        default="",
        verbose_name="Gender",
        help_text="Employee's gender.",
    )

    # ── Marital Status ──────────────────────────────────────────────
    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        blank=True,
        default="",
        verbose_name="Marital Status",
        help_text="Employee's marital status.",
    )
    spouse_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Spouse Name",
        help_text="Name of the employee's spouse.",
    )
    marriage_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Marriage Date",
        help_text="Date of marriage.",
    )

    # ── Active Flag ─────────────────────────────────────────────────
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Is Active",
        help_text="Quick filter for active/inactive employees.",
    )

    # ── Contact Fields ──────────────────────────────────────────────
    email = models.EmailField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Work Email",
        help_text="Official work email address.",
    )
    personal_email = models.EmailField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Personal Email",
        help_text="Personal email address (optional).",
    )
    mobile = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Mobile Phone",
        help_text="Mobile number in +94 XX XXX XXXX format.",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Phone (Landline)",
        help_text="Home or landline number.",
    )
    work_phone = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Work Phone",
        help_text="Office/work phone number.",
    )
    phone_extension = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Phone Extension",
        help_text="Internal phone extension number.",
    )

    # ── Employment Type ─────────────────────────────────────────────
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default=DEFAULT_EMPLOYMENT_TYPE,
        db_index=True,
        verbose_name="Employment Type",
        help_text="Type of employment (full-time, part-time, contract, etc.).",
    )

    # ── Status ──────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=EMPLOYEE_STATUS_CHOICES,
        default=DEFAULT_EMPLOYEE_STATUS,
        db_index=True,
        verbose_name="Status",
        help_text="Current employment status.",
    )

    # ── Department & Designation ──────────────────────────────────
    department = models.ForeignKey(
        "organization.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
        verbose_name="Department",
        help_text="Primary department assignment.",
    )
    designation = models.ForeignKey(
        "organization.Designation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
        verbose_name="Designation",
        help_text="Employee's job designation/position.",
    )

    # ── Manager (Self-referential FK) ───────────────────────────────
    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="direct_reports",
        verbose_name="Manager",
        help_text="Direct manager/reporting supervisor.",
    )

    # ── Employment Dates ────────────────────────────────────────────
    hire_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Hire Date",
        help_text="Date the employee joined the organisation.",
    )
    probation_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Probation End Date",
        help_text="Date probation period ends.",
    )
    confirmation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Confirmation Date",
        help_text="Date of employment confirmation after probation.",
    )

    # ── Work Location ───────────────────────────────────────────────
    work_location = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Work Location",
        help_text="Office or work location name.",
    )
    work_from_home_eligible = models.BooleanField(
        default=False,
        verbose_name="WFH Eligible",
        help_text="Whether employee is eligible for work from home.",
    )
    work_location_type = models.CharField(
        max_length=20,
        choices=WORK_LOCATION_TYPE_CHOICES,
        blank=True,
        default="",
        verbose_name="Work Location Type",
        help_text="Type of work location (office, remote, hybrid, etc.).",
    )

    # ── Termination Fields ──────────────────────────────────────────
    termination_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Termination Date",
        help_text="Date employment was terminated.",
    )
    termination_reason = models.CharField(
        max_length=30,
        choices=TERMINATION_REASON_CHOICES,
        blank=True,
        default="",
        verbose_name="Termination Reason",
        help_text="Reason for termination.",
    )
    termination_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Termination Notes",
        help_text="Additional notes about the termination.",
    )
    exit_interview_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Exit Interview Date",
        help_text="Date of exit interview.",
    )
    exit_interview_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Exit Interview Notes",
        help_text="Notes from exit interview.",
    )
    terminated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="terminated_employees",
        verbose_name="Terminated By",
        help_text="User who processed the termination.",
    )
    final_settlement_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Final Settlement Amount",
        help_text="Amount of final settlement.",
    )
    final_settlement_paid = models.BooleanField(
        default=False,
        verbose_name="Settlement Paid",
        help_text="Whether the final settlement has been paid.",
    )

    # ── Resignation Fields ──────────────────────────────────────────
    resignation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Resignation Date",
        help_text="Date resignation was submitted.",
    )
    resignation_reason = models.TextField(
        blank=True,
        default="",
        verbose_name="Resignation Reason",
        help_text="Reason for resignation.",
    )
    notice_period = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Notice Period (Days)",
        help_text="Notice period in days.",
    )
    notice_period_waived = models.BooleanField(
        default=False,
        verbose_name="Notice Period Waived",
        help_text="Whether the notice period has been waived.",
    )
    last_working_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Last Working Date",
        help_text="Employee's last working date.",
    )
    counter_offer_made = models.BooleanField(
        default=False,
        verbose_name="Counter Offer Made",
        help_text="Whether a counter offer was made.",
    )
    counter_offer_accepted = models.BooleanField(
        default=False,
        verbose_name="Counter Offer Accepted",
        help_text="Whether the counter offer was accepted.",
    )
    resignation_letter_received = models.BooleanField(
        default=False,
        verbose_name="Resignation Letter Received",
        help_text="Whether the resignation letter was received.",
    )

    # ── Notes ───────────────────────────────────────────────────────
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Notes",
        help_text="Internal HR notes about this employee.",
    )

    class Meta:
        db_table = "employees_employee"
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        ordering = ["employee_id"]
        indexes = [
            models.Index(
                fields=["employee_id"],
                name="idx_emp_employee_id",
            ),
            models.Index(
                fields=["status"],
                name="idx_emp_status",
            ),
            models.Index(
                fields=["nic_number"],
                name="idx_emp_nic_number",
            ),
            models.Index(
                fields=["last_name", "first_name"],
                name="idx_emp_name",
            ),
            models.Index(
                fields=["employment_type", "status"],
                name="idx_emp_type_status",
            ),
            models.Index(
                fields=["date_of_birth"],
                name="idx_emp_dob",
            ),
            models.Index(
                fields=["hire_date"],
                name="idx_emp_hire_date",
            ),
        ]

    def __str__(self):
        return f"{self.employee_id}: {self.full_name}"

    @property
    def full_name(self):
        """Return the employee's full name."""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)

    def get_display_name(self):
        """Return preferred name if set, otherwise full name."""
        return self.preferred_name if self.preferred_name else self.full_name

    @property
    def age(self):
        """Calculate current age in years from date_of_birth."""
        if not self.date_of_birth:
            return None
        today = date.today()
        years = today.year - self.date_of_birth.year
        if (today.month, today.day) < (
            self.date_of_birth.month,
            self.date_of_birth.day,
        ):
            years -= 1
        return years

    @property
    def is_minor(self):
        """Return True if employee is under 18."""
        if self.age is None:
            return None
        return self.age < 18

    @property
    def is_active_employee(self):
        """Return True if employee status is active."""
        return self.status == EMPLOYEE_STATUS_ACTIVE

    @property
    def is_terminated(self):
        """Return True if employee is terminated."""
        return self.status == EMPLOYEE_STATUS_TERMINATED

    @property
    def is_resigned(self):
        """Return True if employee has resigned."""
        return self.status == EMPLOYEE_STATUS_RESIGNED

    # ── System Access Properties ────────────────────────────────────

    @property
    def has_system_access(self):
        """Return True if employee has a linked user account."""
        return self.user_id is not None

    # ── Photo Properties & Methods ──────────────────────────────────

    @property
    def photo_url(self):
        """Return profile photo URL or None."""
        if self.profile_photo:
            return self.profile_photo.url
        return None

    @property
    def has_photo(self):
        """Return True if employee has a profile photo."""
        return bool(self.profile_photo)

    def delete_photo(self):
        """Remove the profile photo."""
        if self.profile_photo:
            self.profile_photo.delete(save=False)
            self.profile_photo = None
            self.save(update_fields=["profile_photo", "updated_on"])

    # ── NIC Utility Methods ─────────────────────────────────────────

    def get_nic_type(self):
        """Return 'old' or 'new' based on NIC format, or None."""
        if not self.nic_number:
            return None
        return "new" if len(self.nic_number.strip()) == 12 else "old"

    def extract_dob_from_nic(self):
        """Extract approximate date of birth from NIC number."""
        if not self.nic_number:
            return None
        birth_year = extract_birth_year_from_nic(self.nic_number)
        if birth_year:
            return date(birth_year, 1, 1)
        return None

    def extract_gender_from_nic(self):
        """Extract gender from NIC number."""
        return extract_gender_from_nic(self.nic_number)

    def get_gender_display_icon(self):
        """Return a display icon/symbol for the gender."""
        icons = {
            GENDER_MALE: "♂",
            GENDER_FEMALE: "♀",
        }
        return icons.get(self.gender, "⚧")

    # ── Marriage Properties ─────────────────────────────────────────

    @property
    def has_spouse(self):
        """Return True if employee is married."""
        return self.marital_status == MARITAL_STATUS_MARRIED

    def is_eligible_for_marriage_leave(self):
        """Return True if employee is getting married (and hasn't been married before)."""
        return self.marital_status != MARITAL_STATUS_MARRIED

    # ── Retirement Properties ───────────────────────────────────────

    @property
    def retirement_date(self):
        """Calculate expected retirement date based on DOB and retirement age."""
        if not self.date_of_birth:
            return None
        return self.date_of_birth.replace(
            year=self.date_of_birth.year + RETIREMENT_AGE
        )

    @property
    def years_until_retirement(self):
        """Calculate years remaining until retirement."""
        if not self.retirement_date:
            return None
        delta = self.retirement_date - date.today()
        return max(0, delta.days // 365)

    # ── Tenure Properties ───────────────────────────────────────────

    @property
    def tenure_in_days(self):
        """Calculate tenure in days from hire date."""
        if not self.hire_date:
            return None
        end = self.termination_date or self.last_working_date or date.today()
        return (end - self.hire_date).days

    @property
    def tenure_in_years(self):
        """Calculate tenure in years from hire date."""
        days = self.tenure_in_days
        if days is None:
            return None
        return round(days / 365.25, 1)

    @property
    def is_on_probation(self):
        """Return True if employee is currently on probation."""
        if not self.probation_end_date:
            return False
        return (
            not self.confirmation_date
            and self.probation_end_date >= date.today()
        )

    @property
    def is_confirmed(self):
        """Return True if employee has been confirmed after probation."""
        return self.confirmation_date is not None

    @property
    def days_since_confirmation(self):
        """Return days since confirmation, or None."""
        if not self.confirmation_date:
            return None
        return (date.today() - self.confirmation_date).days

    # ── Notice Period Properties ────────────────────────────────────

    @property
    def is_serving_notice(self):
        """Return True if employee is currently serving notice period."""
        if not self.resignation_date or not self.notice_period:
            return False
        if self.notice_period_waived:
            return False
        notice_end = self.resignation_date + timedelta(days=self.notice_period)
        return date.today() <= notice_end

    @property
    def notice_period_remaining_days(self):
        """Return remaining notice period days, or None."""
        if not self.resignation_date or not self.notice_period:
            return None
        if self.notice_period_waived:
            return 0
        notice_end = self.resignation_date + timedelta(days=self.notice_period)
        remaining = (notice_end - date.today()).days
        return max(0, remaining)

    def clean(self):
        """Validate model data."""
        super().clean()
        errors = {}

        # Validate DOB not in future
        if self.date_of_birth and self.date_of_birth > date.today():
            errors["date_of_birth"] = "Date of birth cannot be in the future."

        # Validate minimum working age (16 years)
        if self.date_of_birth:
            today = date.today()
            age_years = today.year - self.date_of_birth.year
            if (today.month, today.day) < (
                self.date_of_birth.month,
                self.date_of_birth.day,
            ):
                age_years -= 1
            if age_years < 16:
                errors["date_of_birth"] = (
                    "Employee must be at least 16 years old."
                )

        # Cross-validate DOB and NIC birth year
        if self.date_of_birth and self.nic_number:
            nic_year = extract_birth_year_from_nic(self.nic_number)
            if nic_year and nic_year != self.date_of_birth.year:
                errors["date_of_birth"] = (
                    f"Date of birth year ({self.date_of_birth.year}) does not match "
                    f"NIC birth year ({nic_year})."
                )

        # Auto-populate gender from NIC if gender is empty
        if self.nic_number and not self.gender:
            nic_gender = extract_gender_from_nic(self.nic_number)
            if nic_gender:
                self.gender = nic_gender

        # Spouse name required if married
        if self.marital_status == MARITAL_STATUS_MARRIED and not self.spouse_name:
            errors["spouse_name"] = "Spouse name is required when marital status is married."

        # Marriage date not in future
        if self.marriage_date and self.marriage_date > date.today():
            errors["marriage_date"] = "Marriage date cannot be in the future."

        # Hire date not in future
        if self.hire_date and self.hire_date > date.today():
            errors["hire_date"] = "Hire date cannot be in the future."

        # Probation end date must be after hire date
        if self.probation_end_date and self.hire_date:
            if self.probation_end_date <= self.hire_date:
                errors["probation_end_date"] = (
                    "Probation end date must be after hire date."
                )

        # Confirmation date must be on or after hire date
        if self.confirmation_date and self.hire_date:
            if self.confirmation_date < self.hire_date:
                errors["confirmation_date"] = (
                    "Confirmation date cannot be before hire date."
                )

        # Termination date must be on or after hire date
        if self.termination_date and self.hire_date:
            if self.termination_date < self.hire_date:
                errors["termination_date"] = (
                    "Termination date cannot be before hire date."
                )

        # Prevent self-manager
        if self.manager_id and self.pk and self.manager_id == self.pk:
            errors["manager"] = "An employee cannot be their own manager."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Auto-generate employee_id if not set."""
        if not self.employee_id:
            self.employee_id = self._generate_employee_id()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_employee_id(cls):
        """Generate the next employee ID in EMP-XXXX format."""
        from apps.employees.constants import (
            EMPLOYEE_ID_PADDING,
            EMPLOYEE_ID_PREFIX,
        )

        last_employee = (
            cls.objects.order_by("-employee_id")
            .values_list("employee_id", flat=True)
            .first()
        )
        if last_employee:
            try:
                last_number = int(last_employee.split("-")[-1])
            except (ValueError, IndexError):
                last_number = 0
        else:
            last_number = 0

        next_number = last_number + 1
        return f"{EMPLOYEE_ID_PREFIX}-{str(next_number).zfill(EMPLOYEE_ID_PADDING)}"
