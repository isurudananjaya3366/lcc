# Pricing Configuration Guide

## Quick Start

### 1. Setting Up a Product Price

Every product needs a `ProductPrice` record. Create one via the admin panel or API:

```json
POST /api/pricing/product-prices/
{
    "product": "<product-uuid>",
    "base_price": "1500.00",
    "cost_price": "900.00",
    "is_taxable": true,
    "is_tax_inclusive": false,
    "tax_class": "<tax-class-uuid>"
}
```

### 2. Enabling a Sale Price

Set a temporary sale price with an optional date window:

```json
POST /api/pricing/product-prices/<id>/set-sale-price/
{
    "sale_price": "1200.00"
}
```

Or set dates in the full update:

```json
PATCH /api/pricing/product-prices/<id>/
{
    "sale_price": "1200.00",
    "sale_price_start": "2025-01-01T00:00:00Z",
    "sale_price_end": "2025-01-31T23:59:59Z"
}
```

### 3. Variant Pricing

By default, variants inherit the product price. To override:

```json
POST /api/pricing/variant-prices/
{
    "variant": "<variant-uuid>",
    "use_product_price": false,
    "base_price": "1600.00"
}
```

Variants also support price adjustments on top of the product price:

```json
{
  "variant": "<variant-uuid>",
  "use_product_price": true,
  "price_adjustment_type": "PERCENTAGE",
  "price_adjustment_value": "10.00"
}
```

---

## Tax Configuration

### Tax Classes

Tax classes are defined in the Products module. The default for Sri Lanka:

| Tax Class    | Rate   | Description                 |
| ------------ | ------ | --------------------------- |
| Standard VAT | 15.00% | Default rate for most goods |
| Zero-rated   | 0.00%  | Essential items             |
| Exempt       | 0.00%  | Tax-exempt goods            |

### Tax-Inclusive vs Tax-Exclusive

- **Tax-exclusive** (default): Base price does NOT include tax; tax is added at checkout.
- **Tax-inclusive**: Base price already includes tax; tax is extracted for display.

Set `is_tax_inclusive: true` on the ProductPrice to use inclusive pricing.

### SVAT (Simplified VAT)

The TaxCalculator automatically zeroes the tax rate for SVAT-eligible customers when checking out. No manual configuration needed — just ensure the customer record has the appropriate SVAT flag.

### Compound Tax

For multiple tax layers (e.g., VAT + NBT):

```python
from apps.products.pricing.services.tax_calculator import TaxCalculator

calc = TaxCalculator()
layers = [
    {"name": "VAT", "rate": Decimal("15.00")},
    {"name": "NBT", "rate": Decimal("2.00")},
]
total_tax, breakdown = calc.calculate_compound_tax(Decimal("1000.00"), layers)
# total_tax = 173.00 (150 VAT + 23 NBT on compounded base)
```

---

## Volume / Tiered Pricing

### Creating Tiers

```json
POST /api/pricing/tiered-pricing/bulk-create/
{
    "tiers": [
        {"product": "<uuid>", "min_quantity": 1,  "max_quantity": 9,    "tier_price": "100.00", "tier_type": "all_units"},
        {"product": "<uuid>", "min_quantity": 10, "max_quantity": 49,   "tier_price": "90.00",  "tier_type": "all_units"},
        {"product": "<uuid>", "min_quantity": 50, "max_quantity": null, "tier_price": "80.00",  "tier_type": "all_units"}
    ]
}
```

### Tier Types

| Type          | Behavior                                                              |
| ------------- | --------------------------------------------------------------------- |
| `all_units`   | All units priced at the matched tier. Order 20 units → all 20 at ₨90. |
| `incremental` | Graduated pricing. First 9 at ₨100, next 40 at ₨90, remaining at ₨80. |

### Copying Tiers

Copy an existing product's tier structure to another:

```json
POST /api/pricing/tiered-pricing/copy/
{
    "source_product_id": "<uuid>",
    "target_product_id": "<uuid>"
}
```

---

## Scheduled Pricing

### Creating a Scheduled Price

```json
POST /api/pricing/scheduled-prices/
{
    "product": "<uuid>",
    "name": "Weekend Sale",
    "sale_price": "800.00",
    "start_datetime": "2025-02-01T00:00:00Z",
    "end_datetime": "2025-02-02T23:59:59Z",
    "priority": 10
}
```

### Status Lifecycle

```
PENDING  →  ACTIVE  →  EXPIRED
         ↑           ↑
    (start_datetime) (end_datetime)
```

The `update_scheduled_prices` Celery task runs every 5 minutes to transition statuses automatically.

### Priority System

Higher priority wins when multiple schedules overlap. Flash sales default to priority ≥ 100.

### Manual Control

```
POST /api/pricing/scheduled-prices/<id>/activate/
POST /api/pricing/scheduled-prices/<id>/deactivate/
```

---

## Flash Sales

Flash sales are scheduled prices with quantity limits:

```json
POST /api/pricing/flash-sales/
{
    "scheduled_price": {
        "product": "<uuid>",
        "name": "Flash: Limited Stock",
        "sale_price": "500.00",
        "start_datetime": "2025-02-01T10:00:00Z",
        "end_datetime": "2025-02-01T13:00:00Z"
    },
    "max_quantity": 50
}
```

### Urgency Levels

| Level    | Condition                      | When            |
| -------- | ------------------------------ | --------------- |
| Critical | <5% remaining OR <30 min left  | Almost gone     |
| High     | <20% remaining OR <1 hour left | Running low     |
| Medium   | <50% remaining                 | Selling fast    |
| Low      | ≥50% remaining                 | Still available |

### Monitoring

```
GET /api/pricing/flash-sales/<id>/availability/
```

Returns: `is_sold_out`, `quantity_remaining`, `percent_sold`, `urgency_level`, `urgency_message`.

---

## Promotional Pricing

### Creating a Promotion

```json
POST /api/pricing/scheduled-prices/
{
    "name": "20% Off Electronics",
    "discount_type": "percentage_off",
    "discount_value": "20.00",
    "start_datetime": "2025-02-01T00:00:00Z",
    "end_datetime": "2025-02-28T23:59:59Z",
    "min_quantity": 2,
    "max_discount_amount": "5000.00"
}
```

### Discount Types

| Type             | Behavior           | Example               |
| ---------------- | ------------------ | --------------------- |
| `percentage_off` | % off base price   | 20% off ₨1000 = ₨800  |
| `fixed_off`      | Fixed amount off   | ₨200 off ₨1000 = ₨800 |
| `fixed_price`    | Set specific price | Set to ₨750           |

---

## Price Resolution

The `PriceResolutionService` determines the final price shown to customers. Priority order:

1. **Flash Sale** — highest priority, limited stock
2. **Scheduled Price** — time-based overrides
3. **Promotional Price** — condition-based discounts
4. **Sale Price** — standard sale (from ProductPrice)
5. **Base Price** — fallback

### Public Price Lookup

```
GET /api/pricing/lookup/?product_id=<uuid>&quantity=5
```

Response includes effective price, discount info, tax breakdown, and tiered pricing details. Cached for 5 minutes.

### Bulk Lookup

```json
POST /api/pricing/bulk-lookup/
{
    "items": [
        {"product_id": "<uuid>", "quantity": 1},
        {"product_id": "<uuid>", "variant_id": "<uuid>", "quantity": 10}
    ]
}
```

---

## Bulk Price Updates

Update prices across multiple products at once:

```json
POST /api/pricing/bulk-update/
{
    "filters": {"category_id": "<uuid>"},
    "field": "base_price",
    "update_type": "percentage",
    "value": 5,
    "preview": true
}
```

Set `preview: true` to see changes without applying them.

---

## Celery Task Configuration

Ensure your Celery beat schedule includes the pricing tasks. They are auto-registered via `apps.products.pricing.tasks`:

| Task                            | Schedule      | Notes                                   |
| ------------------------------- | ------------- | --------------------------------------- |
| `update_scheduled_prices`       | `*/5 * * * *` | Critical — keeps price statuses current |
| `archive_expired_schedules`     | `0 3 * * *`   | Archives schedules older than 30 days   |
| `cleanup_expired_schedules`     | `0 2 * * 1`   | Deletes schedules older than 90 days    |
| `cleanup_promotional_prices`    | `30 3 * * 0`  | Deletes promos older than 60 days       |
| `cleanup_flash_sales`           | `45 3 * * 0`  | Deletes flash sales older than 14 days  |
| `aggregate_promotion_analytics` | `0 4 * * *`   | Recalculates ROI and conversion metrics |

---

## Troubleshooting

### Price not updating?

1. Check `is_active` on the price record
2. Verify the scheduled price status (run `update_scheduled_prices` task manually)
3. Check for higher-priority overlapping schedules

### Tax incorrect?

1. Verify the `TaxClass` rate
2. Check `is_tax_inclusive` — inclusive prices already contain tax
3. For SVAT customers, tax should be zeroed automatically

### Flash sale not ending?

1. Ensure Celery beat is running
2. Manually call the deactivate endpoint
3. Check if `is_sold_out` was set correctly
