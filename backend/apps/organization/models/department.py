from django.core.validators import MinValueValidator
from django.db import models

from mptt.models import MPTTModel, TreeForeignKey

from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin
from apps.organization.constants import (
    DEFAULT_DEPARTMENT_STATUS,
    DEPARTMENT_STATUS_CHOICES,
)


class Department(UUIDMixin, TimestampMixin, SoftDeleteMixin, MPTTModel):
    """Hierarchical department within a tenant organisation.

    Uses django-mptt for efficient tree queries (ancestors, descendants,
    siblings). Each tenant has its own independent department tree.
    """

    # ── Core Fields ─────────────────────────────────────────────────
    name = models.CharField(
        max_length=100,
        help_text="Department name, e.g. 'Human Resources'.",
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique department code, e.g. 'DEPT-HR'.",
    )
    status = models.CharField(
        max_length=20,
        choices=DEPARTMENT_STATUS_CHOICES,
        default=DEFAULT_DEPARTMENT_STATUS,
        db_index=True,
        help_text="Operational status of the department.",
    )

    # ── Description Fields ──────────────────────────────────────────
    description = models.TextField(
        blank=True,
        default="",
        help_text="Detailed description of department responsibilities.",
    )
    mission_statement = models.TextField(
        blank=True,
        default="",
        help_text="Department mission statement and objectives.",
    )

    # ── Hierarchy (MPTT) ────────────────────────────────────────────
    parent = TreeForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
        help_text="Parent department. Null indicates a root department.",
    )

    # ── Manager ─────────────────────────────────────────────────────
    manager = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_departments",
        help_text="Employee who manages this department.",
    )

    # ── Location Fields ─────────────────────────────────────────────
    location = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Location or campus name, e.g. 'Colombo Head Office'.",
    )
    building = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Building name or number.",
    )
    floor = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Floor information, e.g. '3rd Floor'.",
    )

    # ── Contact Fields ──────────────────────────────────────────────
    email = models.EmailField(
        max_length=100,
        blank=True,
        default="",
        help_text="Department email address.",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Department phone number.",
    )
    extension = models.CharField(
        max_length=10,
        blank=True,
        default="",
        help_text="Internal phone extension.",
    )

    # ── Financial Fields ────────────────────────────────────────────
    cost_center = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Cost center code for financial tracking.",
    )
    annual_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Annual budget amount.",
    )
    currency = models.CharField(
        max_length=3,
        default="LKR",
        help_text="ISO 4217 currency code for the budget.",
    )

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        ordering = ["name"]
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        indexes = [
            models.Index(fields=["code"], name="idx_dept_code"),
            models.Index(fields=["status"], name="idx_dept_status"),
            models.Index(fields=["name"], name="idx_dept_name"),
            models.Index(fields=["parent"], name="idx_dept_parent"),
            models.Index(fields=["manager"], name="idx_dept_manager"),
            models.Index(fields=["cost_center"], name="idx_dept_cost_center"),
            models.Index(fields=["status", "parent"], name="idx_dept_status_parent"),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """Normalize code to uppercase."""
        super().clean()
        if self.code:
            self.code = self.code.upper()

    @property
    def is_root(self):
        """Return True if this is a root department (no parent)."""
        return self.parent_id is None

    @property
    def full_path(self):
        """Return slash-separated path from root to this department."""
        ancestors = self.get_ancestors(include_self=True)
        return " / ".join(a.name for a in ancestors)
