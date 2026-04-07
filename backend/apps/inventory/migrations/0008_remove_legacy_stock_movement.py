"""
Remove legacy StockMovement model.

The original StockMovement from 0001_initial was a config-era placeholder.
SP09 introduces a full-featured replacement in apps.inventory.stock.models.
This migration removes the old model to avoid naming conflicts.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0007_sp09_stock_level_model"),
    ]

    operations = [
        migrations.DeleteModel(
            name="StockMovement",
        ),
    ]
