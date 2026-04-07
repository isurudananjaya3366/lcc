"""
QuoteTemplate model for configurable PDF quote templates.

Tasks 53-57: Template model with header, styling, content,
and layout configuration fields.
"""

from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models

hex_color_validator = RegexValidator(
    regex=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
    message="Enter a valid hex color code (e.g., #2563eb)",
)


class QuoteTemplate(models.Model):
    """Configurable template for quote PDF generation."""

    # ── Choices ──────────────────────────────────────────────────
    FONT_CHOICES = [
        ("Helvetica", "Helvetica"),
        ("Times-Roman", "Times Roman"),
        ("Courier", "Courier"),
    ]
    THEME_CHOICES = [
        ("professional", "Professional"),
        ("modern", "Modern"),
        ("minimal", "Minimal"),
        ("classic", "Classic"),
    ]
    LINE_SPACING_CHOICES = [
        ("compact", "Compact"),
        ("normal", "Normal"),
        ("relaxed", "Relaxed"),
    ]
    ALIGNMENT_CHOICES = [
        ("left", "Left"),
        ("center", "Center"),
        ("right", "Right"),
    ]
    PAGE_SIZE_CHOICES = [
        ("A4", "A4"),
        ("Letter", "Letter"),
        ("Legal", "Legal"),
    ]
    ORIENTATION_CHOICES = [
        ("portrait", "Portrait"),
        ("landscape", "Landscape"),
    ]

    # ── Core Fields (Task 53) ────────────────────────────────────
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="quote_templates",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # ── Header Fields (Task 54) ──────────────────────────────────
    logo = models.ImageField(
        upload_to="quote_templates/logos/",
        null=True,
        blank=True,
    )
    show_logo = models.BooleanField(default=True)
    business_name = models.CharField(max_length=200, blank=True)
    business_address = models.TextField(blank=True)
    business_city = models.CharField(max_length=100, blank=True)
    business_postal_code = models.CharField(max_length=20, blank=True)
    business_country = models.CharField(max_length=100, default="Sri Lanka")
    show_business_address = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email_address = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    show_contact_info = models.BooleanField(default=True)
    company_registration_number = models.CharField(max_length=50, blank=True)
    tax_registration_number = models.CharField(max_length=50, blank=True)

    # ── Styling Fields (Task 55) ─────────────────────────────────
    primary_color = models.CharField(
        max_length=7, default="#2563eb", validators=[hex_color_validator]
    )
    secondary_color = models.CharField(
        max_length=7, default="#64748b", validators=[hex_color_validator]
    )
    accent_color = models.CharField(
        max_length=7, default="#f59e0b", validators=[hex_color_validator]
    )
    text_color = models.CharField(
        max_length=7, default="#1e293b", validators=[hex_color_validator]
    )
    header_font = models.CharField(
        max_length=50, choices=FONT_CHOICES, default="Helvetica"
    )
    body_font = models.CharField(
        max_length=50, choices=FONT_CHOICES, default="Helvetica"
    )
    font_size = models.PositiveIntegerField(
        default=10, validators=[MinValueValidator(8), MaxValueValidator(14)]
    )
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default="professional")
    show_borders = models.BooleanField(default=True)
    show_grid_lines = models.BooleanField(default=False)
    line_spacing = models.CharField(
        max_length=20, choices=LINE_SPACING_CHOICES, default="normal"
    )

    # ── Content Fields (Task 56) ─────────────────────────────────
    footer_text = models.TextField(blank=True)
    show_footer = models.BooleanField(default=True)
    footer_alignment = models.CharField(
        max_length=10, choices=ALIGNMENT_CHOICES, default="center"
    )
    terms_and_conditions = models.TextField(blank=True)
    show_terms = models.BooleanField(default=True)
    terms_title = models.CharField(max_length=100, default="Terms & Conditions")
    default_thank_you_message = models.TextField(
        blank=True, default="Thank you for your business!"
    )
    default_payment_instructions = models.TextField(blank=True)
    validity_message_template = models.CharField(
        max_length=200,
        default="This quotation is valid until {valid_until}",
    )
    show_signature_line = models.BooleanField(default=True)
    signature_label = models.CharField(max_length=100, default="Authorized Signature")
    authorized_person_name = models.CharField(max_length=200, blank=True)
    authorized_person_title = models.CharField(max_length=100, blank=True)

    # ── Layout Fields (Task 57) ──────────────────────────────────
    layout_options = models.JSONField(default=dict, blank=True)
    page_size = models.CharField(
        max_length=20, choices=PAGE_SIZE_CHOICES, default="A4"
    )
    page_orientation = models.CharField(
        max_length=20, choices=ORIENTATION_CHOICES, default="portrait"
    )
    margin_top = models.PositiveIntegerField(default=20, help_text="Top margin in mm")
    margin_bottom = models.PositiveIntegerField(default=20)
    margin_left = models.PositiveIntegerField(default=20)
    margin_right = models.PositiveIntegerField(default=20)

    # ── Timestamps ───────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "quotes_quotetemplate"
        ordering = ["-is_default", "name"]
        verbose_name = "Quote Template"
        verbose_name_plural = "Quote Templates"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "name"],
                name="unique_template_name_per_tenant",
            ),
        ]

    def __str__(self):
        suffix = " (Default)" if self.is_default else ""
        return f"{self.name}{suffix}"

    @classmethod
    def get_default_template(cls, tenant):
        """Return the default template for a tenant, creating one if needed."""
        template = cls.objects.filter(
            tenant=tenant, is_default=True, is_active=True
        ).first()
        if template:
            return template
        template = cls.objects.filter(tenant=tenant, is_active=True).first()
        if template:
            return template
        return cls.objects.create(
            tenant=tenant, name="Default Template", is_default=True
        )

    @staticmethod
    def get_default_layout_options():
        """Return the default layout options structure."""
        return {
            "columns": {
                "item_code": {"visible": True, "order": 1, "width": "15%"},
                "description": {"visible": True, "order": 2, "width": "35%"},
                "quantity": {"visible": True, "order": 3, "width": "10%"},
                "unit_price": {"visible": True, "order": 4, "width": "15%"},
                "discount": {"visible": True, "order": 5, "width": "10%"},
                "tax": {"visible": True, "order": 6, "width": "10%"},
                "total": {"visible": True, "order": 7, "width": "15%"},
            },
            "sections": {
                "header": {"visible": True, "order": 1},
                "customer_info": {"visible": True, "order": 2},
                "line_items": {"visible": True, "order": 3},
                "totals": {"visible": True, "order": 4},
                "terms": {"visible": True, "order": 5},
                "payment_instructions": {"visible": True, "order": 6},
                "signature": {"visible": True, "order": 7},
                "footer": {"visible": True, "order": 8},
            },
            "line_items": {
                "show_item_codes": True,
                "show_descriptions": True,
                "show_notes": True,
                "group_by_category": False,
            },
            "totals": {
                "show_subtotal": True,
                "show_discount": True,
                "show_tax_breakdown": True,
                "show_grand_total": True,
            },
        }

    def get_visible_columns(self):
        """Return list of visible column names sorted by order."""
        columns = self.layout_options.get("columns", {})
        visible = [
            (name, cfg.get("order", 99))
            for name, cfg in columns.items()
            if cfg.get("visible", True)
        ]
        visible.sort(key=lambda x: x[1])
        return [name for name, _ in visible]

    def is_section_visible(self, section_name):
        """Check if a section is visible in layout options."""
        sections = self.layout_options.get("sections", {})
        section = sections.get(section_name, {})
        return section.get("visible", True)

    def save(self, *args, **kwargs):
        # Ensure only one default per tenant
        if self.is_default:
            QuoteTemplate.objects.filter(
                tenant=self.tenant, is_default=True
            ).exclude(pk=self.pk).update(is_default=False)

        # Initialize layout options if empty
        if not self.layout_options:
            self.layout_options = self.get_default_layout_options()

        super().save(*args, **kwargs)
