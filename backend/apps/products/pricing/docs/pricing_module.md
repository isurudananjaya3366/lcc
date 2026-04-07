# Pricing Module Documentation

## Overview

The **Pricing** module (`apps.products.pricing`) provides a comprehensive product pricing system for the LankaCommerce Cloud POS platform. It handles base pricing, tax calculations (with Sri Lankan VAT/SVAT support), tiered/volume pricing, scheduled/promotional pricing, flash sales, and a unified price resolution engine.

---

## Architecture

```
apps/products/pricing/
├── models/               # 10 models across 9 files
│   ├── product_price.py      # ProductPrice — base, sale, wholesale, cost prices
│   ├── variant_price.py      # VariantPrice — per-variant overrides & inheritance
│   ├── price_history.py      # PriceHistory — audit trail via GenericFK
│   ├── tiered_pricing.py     # TieredPricing, VariantTieredPricing — volume discounts
│   ├── scheduled_price.py    # ScheduledPrice — time-based price overrides
│   ├── flash_sale.py         # FlashSale — limited-quantity timed sales
│   ├── promotional_price.py  # PromotionalPrice — condition-based promotions
│   ├── scheduled_price_history.py  # Archive of expired schedules
│   └── promotion_analytics.py     # View/click/conversion tracking
│
├── managers/
│   └── price_manager.py      # ProductPriceManager (extends AliveManager)
│
├── services/
│   ├── tax_calculator.py      # TaxCalculator — VAT, SVAT, compound tax
│   ├── price_calculation.py   # PriceCalculationService — facade
│   ├── bulk_pricing.py        # BulkPricingService — all_units & incremental tiers
│   ├── cart_calculator.py     # CartPriceCalculator — line & cart totals
│   ├── price_resolution.py   # PriceResolutionService — priority-based resolution
│   └── tax_audit.py          # log_tax_calculation for audit trail
│
├── serializers/
│   ├── product_price.py       # ProductPriceSerializer (read/write), VariantPriceSerializer
│   ├── tiered_pricing.py      # TieredPricingSerializer, VariantTieredPricingSerializer
│   ├── scheduled_price.py     # ScheduledPriceSerializer, FlashSaleSerializer
│   └── price_breakdown.py     # PriceBreakdownSerializer (composite read-only)
│
├── views/
│   ├── product_price.py       # ProductPriceViewSet, VariantPriceViewSet
│   ├── tiered_pricing.py      # TieredPricingViewSet, VariantTieredPricingViewSet
│   ├── scheduled_price.py     # ScheduledPriceViewSet, FlashSaleViewSet
│   ├── price_lookup.py        # PriceLookupView (public), BulkPriceLookupView
│   └── bulk_operations.py     # BulkPriceUpdateView
│
├── tasks/                 # Celery beat tasks for schedule management
├── tests/                 # Unit, service, API, and integration tests
├── constants.py           # LKR currency config, price types, choices
├── fields.py              # PriceField (DecimalField with validation)
├── middleware.py          # CurrentUserMiddleware
├── signals.py             # Auto-create PriceHistory on save
├── utils.py               # format_lkr, parse_lkr, round_lkr
├── admin.py               # Admin configuration for all models
└── urls.py                # DefaultRouter + standalone API paths
```

---

## Models

### ProductPrice

One-to-one relationship with `Product`. Stores:

- **base_price** — standard retail price
- **cost_price** — purchase/manufacturing cost
- **sale_price** — discounted price with optional date window
- **wholesale_price** — bulk buyer price with minimum quantity
- **Tax config** — `is_taxable`, `is_tax_inclusive`, FK to `TaxClass`

Key properties: `is_on_sale`, `get_current_price()`, `profit_margin`, `markup_percentage`, `get_price_with_tax()`, `get_tax_breakdown()`.

### VariantPrice

One-to-one on `ProductVariant`. Inherits from product price by default (`use_product_price=True`). Can override any price field. Supports fixed or percentage price adjustments.

### TieredPricing / VariantTieredPricing

Volume discount tiers with two modes:

- **all_units** — entire order at the matched tier price
- **incremental** — graduated (each range at its own tier price)

### ScheduledPrice

Time-based price overrides with priority system. Status lifecycle: PENDING → ACTIVE → EXPIRED. Overlap detection built in.

### FlashSale

Extends ScheduledPrice via OneToOneField. Adds `max_quantity`, `quantity_sold`, urgency levels (critical/high/medium/low). Auto-expires when sold out.

### PromotionalPrice

Condition-based promotions applying to specific products or categories via M2M. Discount types: PERCENTAGE_OFF, FIXED_OFF, FIXED_PRICE. Supports min quantity, min order value, max discount cap.

### PriceHistory

Audit trail using Django's GenericForeignKey. Automatically created by `post_save` signals on ProductPrice and VariantPrice.

---

## Services

### TaxCalculator

Pure-math tax calculations with no DB dependency for core methods:

- Standard tax: `calculate_tax_amount()`, `calculate_price_with_tax()`, `extract_tax_from_inclusive_price()`
- Inclusive ↔ exclusive conversion
- Compound tax: `calculate_compound_tax()` for multi-layer Sri Lankan taxes
- SVAT: `get_effective_tax_rate()` with zero-rate for eligible customers
- Validation: `validate_tax_calculation()`, `validate_inclusive_conversion()`

### BulkPricingService

Processes tiered pricing for a given quantity:

- `calculate_tiered_price(tiers, quantity, base_price)` — returns total, unit price, breakdown, savings
- `get_next_tier_savings()` — shows how many more units to reach the next discount
- `get_tier_summary()` — formatted table of all tiers

### CartPriceCalculator

Combines tiered pricing + tax for shopping cart:

- `calculate_line_item()` — single product line
- `calculate_cart()` — multiple lines with totals

### PriceResolutionService

Priority-based effective price resolution:

1. Flash Sale (highest priority)
2. Scheduled Price
3. Promotional Price
4. Sale Price
5. Base Price (fallback)

Returns: `{price, price_type, reason, original_price, discount_amount, discount_percentage}`

---

## API Endpoints

| Endpoint                               | Method | Auth | Description                 |
| -------------------------------------- | ------ | ---- | --------------------------- |
| `/product-prices/`                     | CRUD   | Yes  | Product price management    |
| `/product-prices/{id}/breakdown/`      | GET    | Yes  | Full price breakdown        |
| `/product-prices/{id}/set-sale-price/` | POST   | Yes  | Quick-set sale price        |
| `/product-prices/bulk-update/`         | POST   | Yes  | Bulk price adjustments      |
| `/variant-prices/`                     | CRUD   | Yes  | Variant price management    |
| `/tiered-pricing/`                     | CRUD   | Yes  | Volume tier management      |
| `/tiered-pricing/bulk-create/`         | POST   | Yes  | Batch tier creation         |
| `/tiered-pricing/copy/`                | POST   | Yes  | Copy tiers between products |
| `/variant-tiered-pricing/`             | CRUD   | Yes  | Variant-level tiers         |
| `/scheduled-prices/`                   | CRUD   | Yes  | Scheduled price management  |
| `/scheduled-prices/{id}/activate/`     | POST   | Yes  | Manual activation           |
| `/scheduled-prices/{id}/deactivate/`   | POST   | Yes  | Manual deactivation         |
| `/scheduled-prices/upcoming/`          | GET    | Yes  | Pending schedules           |
| `/scheduled-prices/active/`            | GET    | Yes  | Currently active            |
| `/scheduled-prices/{id}/conflicts/`    | GET    | Yes  | Overlapping schedules       |
| `/flash-sales/`                        | CRUD   | Yes  | Flash sale management       |
| `/flash-sales/{id}/availability/`      | GET    | Yes  | Stock & urgency info        |
| `/flash-sales/active-now/`             | GET    | Yes  | Active, non-sold-out sales  |
| `/lookup/`                             | GET    | No   | Public price lookup         |
| `/bulk-lookup/`                        | POST   | No   | Multi-item price lookup     |
| `/bulk-update/`                        | POST   | Yes  | Filtered bulk price update  |

---

## Celery Tasks

| Task                            | Schedule       | Purpose                             |
| ------------------------------- | -------------- | ----------------------------------- |
| `update_scheduled_prices`       | Every 5 min    | Activate/expire scheduled prices    |
| `cleanup_expired_schedules`     | Monday 2 AM    | Remove schedules expired >90 days   |
| `archive_expired_schedules`     | Daily 3 AM     | Archive schedules expired >30 days  |
| `cleanup_promotional_prices`    | Sunday 3:30 AM | Remove promos expired >60 days      |
| `cleanup_flash_sales`           | Sunday 3:45 AM | Remove flash sales expired >14 days |
| `aggregate_promotion_analytics` | Daily 4 AM     | Recalculate analytics metrics       |

---

## Currency

All prices use **LKR (Sri Lankan Rupee)**:

- Symbol: ₨
- Decimal places: 2
- Max digits: 12
- Range: 0.00 – 999,999,999.99
- Custom `PriceField` enforces these constraints at the model level

---

## Signals

- `post_save` on `ProductPrice` → creates `PriceHistory` entry
- `post_save` on `VariantPrice` → creates `PriceHistory` entry
