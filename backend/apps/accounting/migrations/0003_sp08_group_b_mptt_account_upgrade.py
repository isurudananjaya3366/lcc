"""
SP08 Group B: Upgrade Account model to MPTT with hierarchy fields.

Adds MPTT tree fields, account_type_config FK, category, status,
is_header, currency, balance fields, and constraints.
"""

from decimal import Decimal
import django.db.models.deletion
from django.db import migrations, models
import mptt.fields


def rebuild_mptt_tree(apps, schema_editor):
    """Rebuild MPTT tree for existing Account rows.

    During migrations, the historical model returned by apps.get_model()
    uses a plain Manager (not TreeManager), so .rebuild() is unavailable.
    We import the real model only when rows exist and need rebuilding.
    """
    Account = apps.get_model("accounting", "Account")
    if not Account.objects.exists():
        return
    from apps.accounting.models import Account as RealAccount

    RealAccount.objects.rebuild()


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0002_sp08_group_a_account_type_config"),
    ]

    operations = [
        # ── 1. Add MPTT fields with defaults for existing rows ──────
        migrations.AddField(
            model_name="account",
            name="level",
            field=models.PositiveIntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="account",
            name="lft",
            field=models.PositiveIntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="account",
            name="rght",
            field=models.PositiveIntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="account",
            name="tree_id",
            field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
            preserve_default=False,
        ),
        # ── 2. Change parent FK to TreeForeignKey + PROTECT ─────────
        migrations.AlterField(
            model_name="account",
            name="parent",
            field=mptt.fields.TreeForeignKey(
                blank=True,
                help_text="Parent account for sub-account hierarchy.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="children",
                to="accounting.account",
                verbose_name="Parent Account",
            ),
        ),
        # ── 3. Add account_type_config FK ───────────────────────────
        migrations.AddField(
            model_name="account",
            name="account_type_config",
            field=models.ForeignKey(
                blank=True,
                help_text="Link to the account type configuration for code range and balance rules.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="accounts",
                to="accounting.accounttypeconfig",
                verbose_name="Account Type Configuration",
            ),
        ),
        # ── 4. Add category field ───────────────────────────────────
        migrations.AddField(
            model_name="account",
            name="category",
            field=models.CharField(
                choices=[
                    ("CURRENT", "Current"),
                    ("NON_CURRENT", "Non-Current"),
                    ("OPERATING", "Operating"),
                    ("NON_OPERATING", "Non-Operating"),
                    ("OWNER_CAPITAL", "Owner Capital"),
                    ("RETAINED_EARNINGS", "Retained Earnings"),
                    ("OTHER", "Other"),
                ],
                db_index=True,
                default="OTHER",
                help_text="Sub-classification within the account type.",
                max_length=30,
                verbose_name="Category",
            ),
        ),
        # ── 5. Add status field ─────────────────────────────────────
        migrations.AddField(
            model_name="account",
            name="status",
            field=models.CharField(
                choices=[
                    ("ACTIVE", "Active"),
                    ("INACTIVE", "Inactive"),
                    ("ARCHIVED", "Archived"),
                ],
                db_index=True,
                default="ACTIVE",
                help_text="Account lifecycle status.",
                max_length=20,
                verbose_name="Status",
            ),
        ),
        # ── 6. Add is_header flag ──────────────────────────────────
        migrations.AddField(
            model_name="account",
            name="is_header",
            field=models.BooleanField(
                default=False,
                help_text="Header/summary accounts group child accounts and cannot hold transactions.",
                verbose_name="Header Account",
            ),
        ),
        # ── 7. Add currency field ──────────────────────────────────
        migrations.AddField(
            model_name="account",
            name="currency",
            field=models.CharField(
                default="LKR",
                help_text="ISO 4217 currency code. Defaults to LKR (Sri Lankan Rupee).",
                max_length=3,
                verbose_name="Currency",
            ),
        ),
        # ── 8. Add opening_balance field ────────────────────────────
        migrations.AddField(
            model_name="account",
            name="opening_balance",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                help_text="Initial balance when the account was created or at fiscal year start.",
                max_digits=20,
                verbose_name="Opening Balance",
            ),
        ),
        # ── 9. Add current_balance field ────────────────────────────
        migrations.AddField(
            model_name="account",
            name="current_balance",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                help_text="Cached current balance, updated by journal entries.",
                max_digits=20,
                verbose_name="Current Balance",
            ),
        ),
        # ── 10. Update is_system help text ──────────────────────────
        migrations.AlterField(
            model_name="account",
            name="is_system",
            field=models.BooleanField(
                default=False,
                help_text="Whether this is a system-generated account that cannot be deleted.",
                verbose_name="System Account",
            ),
        ),
        # ── 11. Add new indexes ─────────────────────────────────────
        migrations.AddIndex(
            model_name="account",
            index=models.Index(fields=["status"], name="idx_account_status"),
        ),
        migrations.AddIndex(
            model_name="account",
            index=models.Index(fields=["tree_id", "lft"], name="idx_account_tree"),
        ),
        # ── 12. Add check constraint ───────────────────────────────
        migrations.AddConstraint(
            model_name="account",
            constraint=models.CheckConstraint(
                condition=models.Q(code__regex=r"^\d{4,}$"),
                name="chk_account_code_numeric",
            ),
        ),
        # ── 13. Rebuild MPTT tree data for existing rows ────────────
        migrations.RunPython(
            code=rebuild_mptt_tree,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
