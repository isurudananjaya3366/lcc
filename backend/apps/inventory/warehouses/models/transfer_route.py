"""
TransferRoute model — inter-warehouse transfer routes.

Defines available pathways for moving inventory between warehouses,
including transit times, distances, and cost estimation.
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class TransferRoute(UUIDMixin, TimestampMixin, models.Model):
    """Route between two warehouses for inventory transfers."""

    source_warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.CASCADE,
        related_name="outgoing_routes",
    )

    destination_warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.CASCADE,
        related_name="incoming_routes",
    )

    # Operational fields
    transit_days = models.PositiveIntegerField(
        default=1,
        help_text="Estimated transit time in days",
    )

    distance_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )

    primary_carrier = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Name of primary transport company",
    )

    notes = models.TextField(blank=True, default="")

    is_preferred = models.BooleanField(
        default=False,
        help_text="Flag this as the preferred route between these warehouses",
    )

    is_active = models.BooleanField(default=True, db_index=True)

    # Cost fields (LKR)
    estimated_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Flat estimated cost (LKR)",
    )

    cost_per_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    cost_per_m3 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    minimum_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Fixed minimum charge (LKR)",
    )

    class Meta:
        app_label = "inventory"
        db_table = "inventory_transfer_routes"
        verbose_name = "Transfer Route"
        verbose_name_plural = "Transfer Routes"
        ordering = ["source_warehouse", "destination_warehouse"]
        constraints = [
            models.UniqueConstraint(
                fields=["source_warehouse", "destination_warehouse"],
                name="uq_transfer_route_src_dst",
            ),
        ]
        indexes = [
            models.Index(fields=["source_warehouse", "is_active"]),
            models.Index(fields=["destination_warehouse", "is_active"]),
        ]

    def __str__(self):
        return (
            f"{self.source_warehouse.code} → {self.destination_warehouse.code} "
            f"({self.transit_days}d)"
        )

    # ── validation ────────────────────────────────────────────────────

    def clean(self):
        super().clean()
        errors = {}
        if (
            self.source_warehouse_id
            and self.destination_warehouse_id
            and self.source_warehouse_id == self.destination_warehouse_id
        ):
            errors["destination_warehouse"] = (
                "Source and destination warehouses must differ."
            )
        if self.transit_days is not None and self.transit_days < 1:
            errors["transit_days"] = "Transit days must be at least 1."
        # Validate both warehouses are active
        if self.source_warehouse_id and hasattr(self, "source_warehouse"):
            try:
                src = self.source_warehouse
                if src and not src.is_status_active():
                    errors["source_warehouse"] = (
                        "Source warehouse must be active."
                    )
            except Exception:
                pass
        if self.destination_warehouse_id and hasattr(self, "destination_warehouse"):
            try:
                dst = self.destination_warehouse
                if dst and not dst.is_status_active():
                    errors["destination_warehouse"] = errors.get(
                        "destination_warehouse",
                        "Destination warehouse must be active.",
                    )
            except Exception:
                pass
        if errors:
            raise ValidationError(errors)

    # ── cost calculation ──────────────────────────────────────────────

    def calculate_transfer_cost(self, weight_kg=0, volume_m3=0):
        """
        Estimate transfer cost for a given weight and/or volume.

        ``total = max(estimated_cost, minimum_cost) + max(weight_cost, volume_cost)``
        """
        base = max(self.estimated_cost, self.minimum_cost)
        weight_cost = Decimal(str(weight_kg)) * self.cost_per_kg
        volume_cost = Decimal(str(volume_m3)) * self.cost_per_m3
        return base + max(weight_cost, volume_cost)
