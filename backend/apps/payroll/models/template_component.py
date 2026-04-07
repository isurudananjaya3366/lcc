from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import UUIDMixin


class TemplateComponent(UUIDMixin, models.Model):
    """Links a SalaryComponent to a SalaryTemplate with default values.

    Defines which components are part of a template and their
    default amounts, plus override constraints for employee-level customization.
    """

    template = models.ForeignKey(
        "payroll.SalaryTemplate",
        on_delete=models.CASCADE,
        related_name="components",
        help_text="The salary template this component belongs to.",
    )
    component = models.ForeignKey(
        "payroll.SalaryComponent",
        on_delete=models.PROTECT,
        related_name="template_usages",
        help_text="The salary component being included.",
    )
    default_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Default amount for this component in this template.",
    )
    can_override = models.BooleanField(
        default=True,
        help_text="Whether this value can be overridden per employee.",
    )
    min_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum allowed value when overriding.",
    )
    max_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum allowed value when overriding.",
    )
    is_mandatory = models.BooleanField(
        default=True,
        help_text="Whether this component must be included in employee salary.",
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Order for display in UI and reports (lower = first).",
    )

    class Meta:
        unique_together = ("template", "component")
        ordering = ["display_order", "component__display_order"]

    def __str__(self):
        return f"{self.template.name} - {self.component.name}"

    def clean(self):
        super().clean()
        if self.min_value is not None and self.max_value is not None:
            if self.min_value > self.max_value:
                raise ValidationError(
                    "Minimum value cannot exceed maximum value."
                )
        if self.default_value and self.min_value is not None:
            if self.default_value < self.min_value:
                raise ValidationError(
                    "Default value cannot be less than minimum value."
                )
        if self.default_value and self.max_value is not None:
            if self.default_value > self.max_value:
                raise ValidationError(
                    "Default value cannot exceed maximum value."
                )
