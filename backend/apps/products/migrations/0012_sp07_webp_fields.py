"""
Add WebP variant paths and placeholder fields to ProductImage and VariantImage.

SP07 Group D — WebP Conversion & Optimization
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0011_sp07_variant_image"),
    ]

    operations = [
        # ── ProductImage WebP fields ────────────────────────────────
        migrations.AddField(
            model_name="productimage",
            name="webp_thumbnail_path",
            field=models.CharField(
                blank=True,
                default="",
                editable=False,
                help_text="Path to 150×150 WebP thumbnail.",
                max_length=500,
            ),
        ),
        migrations.AddField(
            model_name="productimage",
            name="webp_medium_path",
            field=models.CharField(
                blank=True,
                default="",
                editable=False,
                help_text="Path to 500×500 WebP medium image.",
                max_length=500,
            ),
        ),
        migrations.AddField(
            model_name="productimage",
            name="webp_large_path",
            field=models.CharField(
                blank=True,
                default="",
                editable=False,
                help_text="Path to 1000×1000 WebP large image.",
                max_length=500,
            ),
        ),
        migrations.AddField(
            model_name="productimage",
            name="placeholder_data_uri",
            field=models.TextField(
                blank=True,
                default="",
                editable=False,
                help_text="Base64-encoded LQIP for progressive loading.",
            ),
        ),
        # ── VariantImage WebP fields ────────────────────────────────
        migrations.AddField(
            model_name="variantimage",
            name="webp_thumbnail_path",
            field=models.CharField(
                blank=True,
                default="",
                editable=False,
                help_text="Path to 150×150 WebP thumbnail.",
                max_length=500,
            ),
        ),
        migrations.AddField(
            model_name="variantimage",
            name="webp_medium_path",
            field=models.CharField(
                blank=True,
                default="",
                editable=False,
                help_text="Path to 500×500 WebP medium image.",
                max_length=500,
            ),
        ),
        migrations.AddField(
            model_name="variantimage",
            name="webp_large_path",
            field=models.CharField(
                blank=True,
                default="",
                editable=False,
                help_text="Path to 1000×1000 WebP large image.",
                max_length=500,
            ),
        ),
        migrations.AddField(
            model_name="variantimage",
            name="placeholder_data_uri",
            field=models.TextField(
                blank=True,
                default="",
                editable=False,
                help_text="Base64-encoded LQIP for progressive loading.",
            ),
        ),
    ]
