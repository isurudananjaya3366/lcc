"""
Migration for SP03 Receipt and ReceiptSequence models.

Creates:
  - pos_receipt: Generated receipt data per POS transaction
  - pos_receipt_sequence: Daily sequence tracking for receipt numbers
"""

import django.db.models.deletion
import uuid

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pos", "0008_sp03_receipt_template"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── ReceiptSequence ──────────────────────────────────
        migrations.CreateModel(
            name="ReceiptSequence",
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
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this record is active.",
                    ),
                ),
                (
                    "is_deleted",
                    models.BooleanField(
                        default=False,
                        help_text="Soft delete flag.",
                    ),
                ),
                (
                    "date",
                    models.DateField(
                        db_index=True,
                        help_text="Date for this sequence",
                    ),
                ),
                (
                    "current_sequence",
                    models.IntegerField(
                        default=0,
                        help_text="Current sequence number for the date",
                    ),
                ),
            ],
            options={
                "verbose_name": "Receipt Sequence",
                "verbose_name_plural": "Receipt Sequences",
                "db_table": "pos_receipt_sequence",
                "ordering": ["-created_on"],
                "abstract": False,
            },
        ),
        migrations.AddConstraint(
            model_name="receiptsequence",
            constraint=models.UniqueConstraint(
                fields=["date"],
                name="unique_receipt_sequence_per_date",
            ),
        ),
        # ── Receipt ──────────────────────────────────────────
        migrations.CreateModel(
            name="Receipt",
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
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this record is active.",
                    ),
                ),
                (
                    "is_deleted",
                    models.BooleanField(
                        default=False,
                        help_text="Soft delete flag.",
                    ),
                ),
                (
                    "receipt_number",
                    models.CharField(
                        db_index=True,
                        editable=False,
                        help_text="Unique receipt identifier (auto-generated: REC-YYYYMMDD-NNNNN)",
                        max_length=50,
                        unique=True,
                    ),
                ),
                (
                    "cart",
                    models.ForeignKey(
                        db_index=True,
                        help_text="The POS cart this receipt was generated from",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="receipts",
                        to="pos.poscart",
                    ),
                ),
                (
                    "transaction_id",
                    models.UUIDField(
                        blank=True,
                        db_index=True,
                        help_text="External transaction identifier (optional)",
                        null=True,
                    ),
                ),
                (
                    "receipt_type",
                    models.CharField(
                        choices=[
                            ("SALE", "Sale Receipt"),
                            ("REFUND", "Refund Receipt"),
                            ("VOID", "Void Receipt"),
                            ("DUPLICATE", "Duplicate Receipt"),
                        ],
                        db_index=True,
                        default="SALE",
                        help_text="Type of receipt: SALE, REFUND, VOID, or DUPLICATE",
                        max_length=20,
                    ),
                ),
                (
                    "template",
                    models.ForeignKey(
                        blank=True,
                        help_text="Template used to generate this receipt",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="receipts",
                        to="pos.receipttemplate",
                    ),
                ),
                (
                    "generated_at",
                    models.DateTimeField(
                        db_index=True,
                        help_text="When this receipt was generated",
                    ),
                ),
                (
                    "printed_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="When this receipt was last printed (null if never printed)",
                        null=True,
                    ),
                ),
                (
                    "emailed_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="When this receipt was last emailed (null if never emailed)",
                        null=True,
                    ),
                ),
                (
                    "receipt_data",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Complete receipt data in JSON format (immutable after generation)",
                    ),
                ),
                (
                    "original_receipt",
                    models.ForeignKey(
                        blank=True,
                        help_text="Original receipt if this is a duplicate",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="duplicates",
                        to="pos.receipt",
                    ),
                ),
                (
                    "reprint_count",
                    models.IntegerField(
                        default=0,
                        help_text="Number of times this receipt has been reprinted",
                    ),
                ),
                (
                    "generated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="generated_receipts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Receipt",
                "verbose_name_plural": "Receipts",
                "db_table": "pos_receipt",
                "ordering": ["-generated_at"],
                "abstract": False,
            },
        ),
        migrations.AddIndex(
            model_name="receipt",
            index=models.Index(
                fields=["cart", "receipt_type"],
                name="pos_receipt_cart_id_receipt_type_idx",
            ),
        ),
    ]
