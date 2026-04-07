"""
Migration for SP03 Receipt Template model.

Creates the ReceiptTemplate model with all configuration fields:
header, address, item display, totals, payment, footer, QR code,
font settings, and template inheritance support.
"""

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pos", "0007_sp02_audit_fixes"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReceiptTemplate",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "deleted_on",
                    models.DateTimeField(blank=True, null=True),
                ),
                # Core fields
                ("name", models.CharField(max_length=100)),
                (
                    "paper_size",
                    models.CharField(
                        choices=[
                            ("80mm", "Thermal 80mm"),
                            ("58mm", "Thermal 58mm"),
                            ("a4", "A4"),
                        ],
                        default="80mm",
                        max_length=10,
                    ),
                ),
                ("is_default", models.BooleanField(default=False)),
                (
                    "description",
                    models.TextField(blank=True, null=True),
                ),
                # Header - Logo & Business Name
                ("show_logo", models.BooleanField(default=True)),
                (
                    "logo_size",
                    models.CharField(
                        choices=[
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                        ],
                        default="medium",
                        max_length=10,
                    ),
                ),
                (
                    "business_name_override",
                    models.CharField(
                        blank=True, max_length=200, null=True
                    ),
                ),
                (
                    "show_business_name",
                    models.BooleanField(default=True),
                ),
                (
                    "business_name_bold",
                    models.BooleanField(default=True),
                ),
                (
                    "business_name_uppercase",
                    models.BooleanField(default=False),
                ),
                # Header custom text
                (
                    "header_line_1",
                    models.CharField(
                        blank=True, max_length=200, null=True
                    ),
                ),
                (
                    "header_line_2",
                    models.CharField(
                        blank=True, max_length=200, null=True
                    ),
                ),
                (
                    "header_line_3",
                    models.CharField(
                        blank=True, max_length=200, null=True
                    ),
                ),
                (
                    "header_line_1_bold",
                    models.BooleanField(default=False),
                ),
                (
                    "header_line_2_bold",
                    models.BooleanField(default=False),
                ),
                (
                    "header_line_3_bold",
                    models.BooleanField(default=False),
                ),
                # Address display
                ("show_address", models.BooleanField(default=True)),
                ("show_phone", models.BooleanField(default=True)),
                ("show_email", models.BooleanField(default=True)),
                ("show_website", models.BooleanField(default=False)),
                ("show_tax_number", models.BooleanField(default=True)),
                (
                    "address_separator",
                    models.BooleanField(default=True),
                ),
                # Item display
                ("show_sku", models.BooleanField(default=False)),
                ("show_barcode", models.BooleanField(default=False)),
                ("show_category", models.BooleanField(default=False)),
                (
                    "show_tax_per_item",
                    models.BooleanField(default=False),
                ),
                (
                    "show_discount_per_item",
                    models.BooleanField(default=True),
                ),
                (
                    "item_description_length",
                    models.PositiveIntegerField(default=30),
                ),
                (
                    "truncate_description",
                    models.BooleanField(default=True),
                ),
                (
                    "show_unit_price",
                    models.BooleanField(default=True),
                ),
                # Totals display
                ("show_subtotal", models.BooleanField(default=True)),
                (
                    "show_tax_breakdown",
                    models.BooleanField(default=True),
                ),
                (
                    "show_total_tax",
                    models.BooleanField(default=True),
                ),
                (
                    "show_total_discount",
                    models.BooleanField(default=True),
                ),
                ("show_savings", models.BooleanField(default=False)),
                ("show_rounding", models.BooleanField(default=False)),
                (
                    "totals_separator",
                    models.BooleanField(default=True),
                ),
                (
                    "bold_grand_total",
                    models.BooleanField(default=True),
                ),
                # Payment display
                (
                    "show_payment_method",
                    models.BooleanField(default=True),
                ),
                (
                    "show_amount_tendered",
                    models.BooleanField(default=True),
                ),
                (
                    "show_change_given",
                    models.BooleanField(default=True),
                ),
                (
                    "show_balance_due",
                    models.BooleanField(default=False),
                ),
                (
                    "show_card_details",
                    models.BooleanField(default=False),
                ),
                (
                    "payment_separator",
                    models.BooleanField(default=True),
                ),
                # Footer
                (
                    "footer_line_1",
                    models.CharField(
                        blank=True, max_length=200, null=True
                    ),
                ),
                (
                    "footer_line_2",
                    models.CharField(
                        blank=True, max_length=200, null=True
                    ),
                ),
                (
                    "footer_line_3",
                    models.CharField(
                        blank=True, max_length=200, null=True
                    ),
                ),
                (
                    "footer_line_1_bold",
                    models.BooleanField(default=False),
                ),
                (
                    "footer_line_2_bold",
                    models.BooleanField(default=False),
                ),
                (
                    "footer_line_3_bold",
                    models.BooleanField(default=False),
                ),
                (
                    "footer_line_1_center",
                    models.BooleanField(default=True),
                ),
                (
                    "footer_line_2_center",
                    models.BooleanField(default=True),
                ),
                (
                    "footer_line_3_center",
                    models.BooleanField(default=True),
                ),
                (
                    "footer_separator",
                    models.BooleanField(default=True),
                ),
                # Return policy
                (
                    "return_policy_text",
                    models.TextField(
                        blank=True,
                        default="Items may be returned within 7 days of purchase with original receipt and tags attached.",
                        null=True,
                    ),
                ),
                # QR code
                ("show_qr_code", models.BooleanField(default=False)),
                (
                    "qr_content_type",
                    models.CharField(
                        choices=[
                            ("transaction_id", "Transaction ID"),
                            ("digital_receipt", "Digital Receipt URL"),
                            ("loyalty", "Loyalty Program"),
                            ("feedback", "Feedback Form"),
                            ("payment_verify", "Payment Verification"),
                            ("website", "Website"),
                        ],
                        default="transaction_id",
                        max_length=20,
                    ),
                ),
                (
                    "qr_code_size",
                    models.CharField(
                        choices=[
                            ("small", "Small"),
                            ("medium", "Medium"),
                            ("large", "Large"),
                        ],
                        default="medium",
                        max_length=10,
                    ),
                ),
                (
                    "qr_label",
                    models.CharField(
                        blank=True, max_length=100, null=True
                    ),
                ),
                (
                    "qr_position",
                    models.CharField(
                        choices=[
                            ("before_footer", "Before Footer"),
                            ("after_footer", "After Footer"),
                        ],
                        default="after_footer",
                        max_length=20,
                    ),
                ),
                # Font settings
                (
                    "font_size",
                    models.CharField(
                        choices=[
                            ("small", "Small"),
                            ("normal", "Normal"),
                            ("large", "Large"),
                        ],
                        default="normal",
                        max_length=10,
                    ),
                ),
                (
                    "header_font_size",
                    models.CharField(
                        choices=[
                            ("small", "Small"),
                            ("normal", "Normal"),
                            ("large", "Large"),
                        ],
                        default="large",
                        max_length=10,
                    ),
                ),
                (
                    "footer_font_size",
                    models.CharField(
                        choices=[
                            ("small", "Small"),
                            ("normal", "Normal"),
                            ("large", "Large"),
                        ],
                        default="normal",
                        max_length=10,
                    ),
                ),
                (
                    "use_bold_headers",
                    models.BooleanField(default=True),
                ),
                (
                    "separator_style",
                    models.CharField(
                        choices=[
                            ("equals", "Equals (═)"),
                            ("dashes", "Dashes (─)"),
                            ("stars", "Stars (*)"),
                            ("none", "None"),
                        ],
                        default="equals",
                        max_length=10,
                    ),
                ),
                (
                    "separator_length",
                    models.CharField(
                        choices=[
                            ("full", "Full Width"),
                            ("half", "Half Width"),
                        ],
                        default="full",
                        max_length=10,
                    ),
                ),
                # Inheritance
                (
                    "is_system_default",
                    models.BooleanField(default=False),
                ),
                (
                    "inherits_from_parent",
                    models.BooleanField(default=True),
                ),
                (
                    "parent_template",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="child_templates",
                        to="pos.receipttemplate",
                    ),
                ),
            ],
            options={
                "verbose_name": "Receipt Template",
                "verbose_name_plural": "Receipt Templates",
                "db_table": "pos_receipt_template",
                "ordering": ["name"],
                "abstract": False,
            },
        ),
    ]
