"""
SP09 Group A: Rename legacy JournalEntry → LegacyJournalEntry and
create the new JournalEntry header model with entry numbering,
type/status/source enums, cached totals, user tracking, and
reversal FK.
"""

import uuid

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0004_sp08_group_d_coa_template"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── Step 1: Rename old JournalEntry → LegacyJournalEntry ─
        migrations.RenameModel(
            old_name="JournalEntry",
            new_name="LegacyJournalEntry",
        ),
        # ── Step 2: Create new JournalEntry header model ─────────
        migrations.CreateModel(
            name="JournalEntry",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Unique identifier (UUID v4).",
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "entry_number",
                    models.CharField(
                        db_index=True,
                        editable=False,
                        help_text="Auto-generated entry number (format: JE-YYYY-NNNNN).",
                        max_length=20,
                        unique=True,
                        verbose_name="Entry Number",
                    ),
                ),
                (
                    "entry_date",
                    models.DateField(
                        db_index=True,
                        help_text="Transaction date of the journal entry.",
                        verbose_name="Entry Date",
                    ),
                ),
                (
                    "entry_type",
                    models.CharField(
                        choices=[
                            ("MANUAL", "Manual Entry"),
                            ("AUTO", "Auto-Generated"),
                            ("ADJUSTING", "Adjusting Entry"),
                            ("REVERSING", "Reversing Entry"),
                        ],
                        db_index=True,
                        default="MANUAL",
                        help_text="Type of journal entry (Manual, Auto, Adjusting, Reversing).",
                        max_length=20,
                        verbose_name="Entry Type",
                    ),
                ),
                (
                    "entry_status",
                    models.CharField(
                        choices=[
                            ("DRAFT", "Draft"),
                            ("PENDING_APPROVAL", "Pending Approval"),
                            ("APPROVED", "Approved"),
                            ("POSTED", "Posted"),
                            ("VOID", "Void"),
                        ],
                        db_index=True,
                        default="DRAFT",
                        help_text="Lifecycle status of the journal entry.",
                        max_length=20,
                        verbose_name="Entry Status",
                    ),
                ),
                (
                    "entry_source",
                    models.CharField(
                        choices=[
                            ("SALES", "Sales"),
                            ("PURCHASE", "Purchase"),
                            ("PAYROLL", "Payroll"),
                            ("INVENTORY", "Inventory"),
                            ("BANKING", "Banking"),
                            ("MANUAL", "Manual Entry"),
                            ("ADJUSTMENT", "Adjustment"),
                        ],
                        db_index=True,
                        default="MANUAL",
                        help_text="Origin/source system of the journal entry.",
                        max_length=20,
                        verbose_name="Source",
                    ),
                ),
                (
                    "reference",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="Source document reference (e.g. Invoice #, PO #).",
                        max_length=50,
                        null=True,
                        verbose_name="Reference",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Transaction narration or memo.",
                        verbose_name="Description",
                    ),
                ),
                (
                    "total_debit",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        editable=False,
                        help_text="Total debit amount (cached from lines).",
                        max_digits=15,
                        verbose_name="Total Debit",
                    ),
                ),
                (
                    "total_credit",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        editable=False,
                        help_text="Total credit amount (cached from lines).",
                        max_digits=15,
                        verbose_name="Total Credit",
                    ),
                ),
                (
                    "posted_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="Timestamp when this entry was posted.",
                        null=True,
                        verbose_name="Posted At",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Timestamp when this record was created.",
                        verbose_name="Created At",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Timestamp when this record was last updated.",
                        verbose_name="Updated At",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        help_text="User who created this journal entry.",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="journal_entries_created",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created By",
                    ),
                ),
                (
                    "posted_by",
                    models.ForeignKey(
                        blank=True,
                        help_text="User who posted this journal entry.",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="journal_entries_posted",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Posted By",
                    ),
                ),
                (
                    "reversal_of",
                    models.ForeignKey(
                        blank=True,
                        help_text="Links this reversal entry to the original entry.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reversed_by",
                        to="accounting.journalentry",
                        verbose_name="Reversal Of",
                    ),
                ),
            ],
            options={
                "verbose_name": "Journal Entry",
                "verbose_name_plural": "Journal Entries",
                "db_table": "accounting_journal_entry",
                "ordering": ["-entry_date", "-entry_number"],
            },
        ),
        # ── Step 3: Add indexes for the new model ─────────────────
        migrations.AddIndex(
            model_name="journalentry",
            index=models.Index(
                fields=["entry_date", "entry_number"],
                name="idx_je_date_number",
            ),
        ),
        migrations.AddIndex(
            model_name="journalentry",
            index=models.Index(
                fields=["entry_status", "entry_date"],
                name="idx_je_status_date",
            ),
        ),
        migrations.AddIndex(
            model_name="journalentry",
            index=models.Index(
                fields=["entry_type"],
                name="idx_je_type",
            ),
        ),
        migrations.AddIndex(
            model_name="journalentry",
            index=models.Index(
                fields=["entry_source"],
                name="idx_je_source",
            ),
        ),
        migrations.AddIndex(
            model_name="journalentry",
            index=models.Index(
                fields=["reference"],
                name="idx_je_reference",
            ),
        ),
    ]
