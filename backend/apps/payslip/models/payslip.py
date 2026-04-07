"""Payslip model for managing generated payslip documents."""

from django.conf import settings
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin
from apps.payslip.constants import PayslipStatus


def payslip_upload_to(instance, filename):
    """Generate dynamic upload path for payslip PDFs.

    Path format: payslips/{year}/{month}/{slip_number}.pdf
    """
    if instance.payroll_period:
        year = instance.payroll_period.period_year
        month = instance.payroll_period.period_month
    else:
        from django.utils import timezone

        now = timezone.now()
        year = now.year
        month = now.month
    return f"payslips/{year}/{month:02d}/{instance.slip_number}.pdf"


class PayslipManager(models.Manager):
    """Custom manager for Payslip model."""

    def for_employee(self, employee):
        """Return payslips for a specific employee."""
        return self.filter(employee=employee)

    def for_period(self, payroll_period):
        """Return payslips for a specific payroll period."""
        return self.filter(payroll_period=payroll_period)

    def pending_generation(self):
        """Return payslips awaiting PDF generation."""
        return self.filter(status=PayslipStatus.DRAFT)

    def pending_email(self):
        """Return generated payslips not yet emailed."""
        return self.filter(
            status=PayslipStatus.GENERATED,
            email_sent=False,
        )


class Payslip(UUIDMixin, TimestampMixin, models.Model):
    """Represents a generated payslip document for an employee.

    Links to the source payroll data (employee, period, employee_payroll)
    and tracks the full lifecycle: generation, distribution, viewing,
    and downloading.
    """

    # ── Relationships ────────────────────────────────────────
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="payslips",
        db_index=True,
        help_text="Employee this payslip belongs to.",
    )
    payroll_period = models.ForeignKey(
        "payroll.PayrollPeriod",
        on_delete=models.CASCADE,
        related_name="payslips",
        db_index=True,
        help_text="Payroll period this payslip covers.",
    )
    employee_payroll = models.ForeignKey(
        "payroll.EmployeePayroll",
        on_delete=models.CASCADE,
        related_name="payslips",
        db_index=True,
        help_text="Source payroll calculation data.",
    )

    # ── Identification ───────────────────────────────────────
    slip_number = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        help_text="Auto-generated slip number (PAY-YYYY-MM-NNN).",
    )

    # ── Status ───────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=PayslipStatus.choices,
        default=PayslipStatus.DRAFT,
        db_index=True,
        help_text="Current lifecycle status of the payslip.",
    )

    # ── Generation Tracking ──────────────────────────────────
    generated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the PDF was generated.",
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_payslips",
        help_text="User who triggered PDF generation.",
    )

    # ── PDF File Storage ─────────────────────────────────────
    pdf_file = models.FileField(
        upload_to=payslip_upload_to,
        null=True,
        blank=True,
        help_text="Generated PDF payslip document.",
    )

    # ── Email Distribution Tracking ──────────────────────────
    email_sent = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether the payslip email has been sent.",
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the payslip email was sent.",
    )
    sent_to = models.EmailField(
        null=True,
        blank=True,
        help_text="Email address the payslip was sent to.",
    )

    # ── View Tracking ────────────────────────────────────────
    first_viewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the employee first viewed this payslip.",
    )
    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times the employee viewed this payslip.",
    )

    # ── Download Tracking ────────────────────────────────────
    first_downloaded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the employee first downloaded this payslip.",
    )
    download_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times the employee downloaded this payslip.",
    )

    objects = PayslipManager()

    class Meta:
        app_label = "payslip"
        db_table = "payslip_payslip"
        verbose_name = "Payslip"
        verbose_name_plural = "Payslips"
        ordering = ["-payroll_period__period_year", "-payroll_period__period_month"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "payroll_period"],
                name="unique_employee_payroll_period_payslip",
            ),
        ]
        indexes = [
            models.Index(
                fields=["status", "email_sent"],
                name="idx_payslip_status_email",
            ),
        ]

    def __str__(self):
        return f"{self.slip_number} - {self.employee}"

    # ── Properties ───────────────────────────────────────────

    @property
    def pdf_url(self):
        """Return URL for PDF file if it exists."""
        if self.pdf_file:
            return self.pdf_file.url
        return None

    @property
    def has_pdf(self):
        """Check if PDF file has been generated."""
        return bool(self.pdf_file)

    # ── Methods ──────────────────────────────────────────────

    def generate_slip_number(self):
        """Generate a unique slip number in PAY-YYYY-MM-NNN format."""
        year = self.payroll_period.period_year
        month = self.payroll_period.period_month

        last_payslip = (
            Payslip.objects.filter(
                payroll_period=self.payroll_period,
            )
            .exclude(pk=self.pk)
            .order_by("-slip_number")
            .first()
        )

        if last_payslip and last_payslip.slip_number:
            try:
                last_seq = int(last_payslip.slip_number.split("-")[-1])
                seq = last_seq + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1

        self.slip_number = f"PAY-{year}-{month:02d}-{seq:03d}"

    def record_view(self):
        """Record an employee view of this payslip."""
        from django.utils import timezone

        if self.first_viewed_at is None:
            self.first_viewed_at = timezone.now()
        self.view_count += 1
        if self.status in (PayslipStatus.GENERATED, PayslipStatus.SENT):
            self.status = PayslipStatus.VIEWED
        self.save(update_fields=["first_viewed_at", "view_count", "status"])

    def record_download(self):
        """Record an employee download of this payslip."""
        from django.utils import timezone

        if self.first_downloaded_at is None:
            self.first_downloaded_at = timezone.now()
        self.download_count += 1
        if self.status != PayslipStatus.DOWNLOADED:
            self.status = PayslipStatus.DOWNLOADED
        self.save(
            update_fields=["first_downloaded_at", "download_count", "status"]
        )

    def mark_generated(self, user=None):
        """Mark payslip as generated after PDF creation."""
        from django.utils import timezone

        self.status = PayslipStatus.GENERATED
        self.generated_at = timezone.now()
        self.generated_by = user
        self.save(update_fields=["status", "generated_at", "generated_by"])

    def mark_sent(self, email_address):
        """Mark payslip as sent after email delivery."""
        from django.utils import timezone

        self.status = PayslipStatus.SENT
        self.email_sent = True
        self.sent_at = timezone.now()
        self.sent_to = email_address
        self.save(update_fields=["status", "email_sent", "sent_at", "sent_to"])

    def save(self, *args, **kwargs):
        """Auto-generate slip number on first save if not set."""
        if not self.slip_number:
            self.generate_slip_number()
        super().save(*args, **kwargs)
