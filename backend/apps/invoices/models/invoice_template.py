"""
Invoice template model — per-tenant PDF customization settings.
"""

from django.db import models


class InvoiceTemplate(models.Model):
    """Stores PDF template configuration and branding for a tenant."""

    FONT_CHOICES = [
        ("Arial", "Arial"),
        ("Helvetica", "Helvetica"),
        ("Times", "Times New Roman"),
        ("Courier", "Courier"),
        ("Noto Sans", "Noto Sans (Unicode)"),
        ("Roboto", "Roboto"),
    ]
    PAGE_SIZE_CHOICES = [
        ("A4", "A4 (210 x 297 mm)"),
        ("Letter", "Letter (8.5 x 11 in)"),
    ]
    ORIENTATION_CHOICES = [
        ("portrait", "Portrait"),
        ("landscape", "Landscape"),
    ]

    # ── Core ──
    tenant = models.OneToOneField(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="invoice_template",
    )
    name = models.CharField(max_length=100, default="Default Template")
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=True)

    # ── Header / Business Info ──
    logo = models.ImageField(
        upload_to="invoice_templates/logos/",
        null=True,
        blank=True,
        help_text="Company logo (recommended: 200x100px)",
    )
    business_name = models.CharField(max_length=200, blank=True)
    business_address = models.TextField(blank=True)
    business_phone = models.CharField(max_length=20, blank=True)
    business_email = models.EmailField(blank=True)
    business_website = models.URLField(blank=True)
    business_registration_number = models.CharField(max_length=50, blank=True)
    vat_registration_number = models.CharField(max_length=50, blank=True)
    svat_registration_number = models.CharField(max_length=50, blank=True)

    # ── Display Toggles ──
    show_logo = models.BooleanField(default=True)
    show_brn = models.BooleanField(default=True)
    show_vat = models.BooleanField(default=True)
    show_website = models.BooleanField(default=False)

    # ── Colors ──
    primary_color = models.CharField(max_length=7, default="#007bff")
    accent_color = models.CharField(max_length=7, default="#6c757d")
    text_color = models.CharField(max_length=7, default="#212529")
    background_color = models.CharField(max_length=7, default="#ffffff")

    # ── Font ──
    font_family = models.CharField(max_length=50, choices=FONT_CHOICES, default="Arial")
    font_size = models.IntegerField(default=10)
    heading_font_size = models.IntegerField(default=14)

    # ── Page Layout ──
    page_size = models.CharField(max_length=10, choices=PAGE_SIZE_CHOICES, default="A4")
    page_orientation = models.CharField(max_length=10, choices=ORIENTATION_CHOICES, default="portrait")
    margin_top = models.IntegerField(default=20, help_text="Top margin in mm")
    margin_bottom = models.IntegerField(default=20, help_text="Bottom margin in mm")
    margin_left = models.IntegerField(default=15, help_text="Left margin in mm")
    margin_right = models.IntegerField(default=15, help_text="Right margin in mm")

    # ── Style Options ──
    use_borders = models.BooleanField(default=True)
    use_shading = models.BooleanField(default=True)
    show_grid = models.BooleanField(default=False)

    # ── Bank Details (Footer) ──
    bank_name = models.CharField(max_length=100, blank=True)
    account_name = models.CharField(max_length=200, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    branch = models.CharField(max_length=100, blank=True)
    swift_code = models.CharField(max_length=20, blank=True)

    # ── Payment & Terms ──
    payment_instructions = models.TextField(
        blank=True,
        default=(
            "Please make payment via bank transfer to the account details shown above. "
            "Include invoice number as payment reference."
        ),
    )
    terms_and_conditions = models.TextField(
        blank=True,
        default=(
            "1. Payment is due within the specified period.\n"
            "2. Late payments may incur additional charges.\n"
            "3. Goods remain property of seller until full payment received."
        ),
    )

    # ── Signature ──
    signature_image = models.ImageField(
        upload_to="invoice_templates/signatures/",
        null=True,
        blank=True,
    )
    authorized_signatory = models.CharField(max_length=100, blank=True)
    signatory_designation = models.CharField(max_length=100, blank=True)

    # ── Footer Toggles ──
    show_bank_details = models.BooleanField(default=True)
    show_terms = models.BooleanField(default=True)
    show_signature = models.BooleanField(default=False)
    footer_text = models.TextField(blank=True)

    # ── Timestamps ──
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "invoice_templates"
        ordering = ["-is_default", "name"]
        verbose_name = "Invoice Template"
        verbose_name_plural = "Invoice Templates"

    def __str__(self):
        tenant_name = getattr(self.tenant, "name", "")
        return f"{tenant_name} - {self.name}" if tenant_name else self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("invoices:template-detail", kwargs={"pk": self.pk})
