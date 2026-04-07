"""
Migration: Upgrade Category model to use django-mptt.

Adds MPTT tree fields (lft, rght, tree_id, level), renames sort_order
to display_order, adds icon and SEO fields, changes parent FK to
TreeForeignKey, and updates indexes/ordering.
"""

import django.db.models.deletion
import mptt.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        # ── 1. Rename sort_order → display_order ────────────────────
        migrations.RenameField(
            model_name="category",
            old_name="sort_order",
            new_name="display_order",
        ),
        # ── 2. Add MPTT tree fields ─────────────────────────────────
        migrations.AddField(
            model_name="category",
            name="lft",
            field=models.PositiveIntegerField(
                default=0, editable=False, db_index=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="category",
            name="rght",
            field=models.PositiveIntegerField(
                default=0, editable=False, db_index=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="category",
            name="tree_id",
            field=models.PositiveIntegerField(
                default=0, editable=False, db_index=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="category",
            name="level",
            field=models.PositiveIntegerField(
                default=0, editable=False, db_index=True
            ),
            preserve_default=False,
        ),
        # ── 3. Add new fields ───────────────────────────────────────
        migrations.AddField(
            model_name="category",
            name="icon",
            field=models.CharField(
                blank=True,
                default="",
                help_text="CSS icon class (e.g., 'fas fa-mobile-alt').",
                max_length=100,
                verbose_name="Icon Class",
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="seo_title",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Custom meta title for search engines. 60 chars optimal.",
                max_length=100,
                verbose_name="SEO Title",
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="seo_description",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Meta description for search result snippets. 155 chars optimal.",
                max_length=200,
                verbose_name="SEO Description",
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="seo_keywords",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Comma-separated keywords for legacy SEO use.",
                max_length=255,
                verbose_name="SEO Keywords",
            ),
        ),
        # ── 4. Change parent FK to TreeForeignKey ───────────────────
        migrations.AlterField(
            model_name="category",
            name="parent",
            field=mptt.fields.TreeForeignKey(
                blank=True,
                help_text="Parent category. Null for root categories.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="products.category",
                verbose_name="Parent Category",
            ),
        ),
        # ── 5. Remove old indexes ───────────────────────────────────
        migrations.RemoveIndex(
            model_name="category",
            name="idx_category_active_sort",
        ),
        # ── 6. Add updated indexes ──────────────────────────────────
        migrations.AddIndex(
            model_name="category",
            index=models.Index(
                fields=["is_active", "display_order"],
                name="idx_category_active_order",
            ),
        ),
        migrations.AddIndex(
            model_name="category",
            index=models.Index(
                fields=["tree_id", "lft"],
                name="idx_category_tree_lft",
            ),
        ),
        # ── 7. Update Meta ordering ─────────────────────────────────
        migrations.AlterModelOptions(
            name="category",
            options={
                "db_table": "products_category",
                "ordering": ["tree_id", "lft"],
                "verbose_name": "Category",
                "verbose_name_plural": "Categories",
            },
        ),
    ]
