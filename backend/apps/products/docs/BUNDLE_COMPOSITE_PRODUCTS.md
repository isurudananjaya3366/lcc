# Bundle & Composite Products (SP05)

> **Phase 04** — ERP Core Modules Part 1
> **SubPhase 05** — Bundle & Composite Products

---

## Overview

This module adds two product composition patterns to LankaCommerce Cloud:

| Pattern                      | Model                          | Use Case                                                                               |
| ---------------------------- | ------------------------------ | -------------------------------------------------------------------------------------- |
| **Bundle**                   | `ProductBundle` + `BundleItem` | Sell existing products together (e.g., Gift Hamper = Chocolate + Wine + Card)          |
| **Composite / Manufactured** | `BillOfMaterials` + `BOMItem`  | Manufacture new products from raw materials (e.g., Custom Cake = Flour + Sugar + Eggs) |

---

## Bundle Products

### Bundle Types

| Type      | Pricing Behaviour                            |
| --------- | -------------------------------------------- |
| `FIXED`   | Bundle sold at a predetermined `fixed_price` |
| `DYNAMIC` | Price = sum of component prices − discount   |

### Discount Types

| Type         | Behaviour                        |
| ------------ | -------------------------------- |
| `PERCENTAGE` | Discount as % of component total |
| `FIXED`      | Flat discount amount (Rs.)       |
| `NONE`       | No discount applied              |

### Creating a Bundle

```python
from apps.products.models import Product, ProductBundle, BundleItem
from apps.products.constants import BUNDLE_TYPE, DISCOUNT_TYPE, PRODUCT_TYPES

# 1. Create the parent product
product = Product.objects.create(
    name="Lanka Tea Gift Set",
    category=category,
    product_type=PRODUCT_TYPES.BUNDLE,
)

# 2. Create the bundle configuration
bundle = ProductBundle.objects.create(
    product=product,
    bundle_type=BUNDLE_TYPE.DYNAMIC,
    discount_type=DISCOUNT_TYPE.PERCENTAGE,
    discount_value=10,  # 10% off
)

# 3. Add component items
BundleItem.objects.create(bundle=bundle, product=ceylon_tea, quantity=2)
BundleItem.objects.create(bundle=bundle, product=tea_strainer, quantity=1)
BundleItem.objects.create(bundle=bundle, product=gift_box, quantity=1, is_optional=True)
```

### Stock Availability

Bundle stock is determined by the **minimum** number of complete bundles that can be assembled from component stock. Only **required** (non-optional) items are considered.

```python
from apps.products.services import BundleStockService

service = BundleStockService(bundle)
available = service.get_available_stock()     # int: complete bundles available
can_fill = service.check_availability(5)      # bool: can we fill 5 bundles?
limiting = service.get_limiting_item()        # dict: bottleneck component
service.reserve_stock(2)                      # atomically reserve 2 bundles
```

### Pricing

```python
from apps.products.services import BundlePricingService

service = BundlePricingService(bundle)
price       = service.get_bundle_price()      # effective price (fixed or dynamic)
individual  = service.get_individual_total()   # sum without discount
savings     = service.get_savings()            # individual − bundle price
```

---

## Composite / Manufactured Products (BOM)

### BOM Structure

A **Bill of Materials** defines the recipe for manufacturing a composite product:

- **Product** — the finished product
- **Version** — BOM version identifier (e.g., "1.0", "2.0")
- **Yield Quantity** — units produced per batch
- **BOM Items** — raw materials with quantities, wastage, and substitutes

### Creating a BOM

```python
from apps.products.models import Product, BillOfMaterials, BOMItem
from apps.products.constants import PRODUCT_TYPES

# Finished product
cake = Product.objects.create(
    name="Birthday Cake",
    category=category,
    product_type=PRODUCT_TYPES.COMPOSITE,
)

# BOM recipe
bom = BillOfMaterials.objects.create(
    product=cake,
    version="1.0",
    yield_quantity=10,
    notes="Standard recipe",
)

# Raw materials
BOMItem.objects.create(
    bom=bom, raw_material=flour,
    quantity=Decimal("2.000"), wastage_percent=Decimal("5.00"),
    is_critical=True,
)
BOMItem.objects.create(
    bom=bom, raw_material=sugar,
    quantity=Decimal("1.000"), wastage_percent=Decimal("0.00"),
    substitute=alternative_sugar,
)
```

### Cost Calculation

```
Material Cost  = Σ (cost_price × quantity)
Wastage Cost   = Σ (cost_price × quantity × wastage% / 100)
Labor Cost     = fixed per batch
Overhead       = fixed amount  OR  % of (material + wastage)
─────────────────────────────────────
Total Cost     = Material (with wastage) + Labor + Overhead
Unit Cost      = Total Cost / yield_quantity
Selling Price  = Unit Cost × (1 + margin%)
```

```python
from apps.products.services import CostCalculationService

service = CostCalculationService(
    bom,
    labor_cost=Decimal("50.00"),
    overhead_percent=Decimal("10.00"),
)

material = service.calculate_material_cost()   # raw material total
with_waste = service.calculate_with_wastage()  # material + wastage
total = service.calculate_total_cost()         # material + labor + overhead
unit = service.calculate_unit_cost()           # total / yield
result = service.suggest_selling_price(50)     # 50% markup
# result = {"unit_cost": ..., "selling_price": ..., "margin_percent": 50}
```

### Manufacturing Stock Check

```python
from apps.products.services import ManufacturingStockService

service = ManufacturingStockService(bom)
materials = service.check_raw_materials()   # list of availability dicts
max_units = service.get_producible_quantity()  # max finished units possible
```

---

## API Endpoints

All endpoints require authentication and are scoped to the active tenant.

### Bundles

| Method    | Endpoint                                   | Description              |
| --------- | ------------------------------------------ | ------------------------ |
| GET       | `/api/products/bundles/`                   | List bundles             |
| POST      | `/api/products/bundles/`                   | Create bundle            |
| GET       | `/api/products/bundles/{id}/`              | Bundle detail            |
| PUT/PATCH | `/api/products/bundles/{id}/`              | Update bundle            |
| DELETE    | `/api/products/bundles/{id}/`              | Delete bundle            |
| GET       | `/api/products/bundles/{id}/availability/` | Check stock availability |
| GET       | `/api/products/bundles/{id}/pricing/`      | Get pricing breakdown    |

### Bundle Items

| Method    | Endpoint                           | Description        |
| --------- | ---------------------------------- | ------------------ |
| GET       | `/api/products/bundle-items/`      | List items         |
| POST      | `/api/products/bundle-items/`      | Add item to bundle |
| PUT/PATCH | `/api/products/bundle-items/{id}/` | Update item        |
| DELETE    | `/api/products/bundle-items/{id}/` | Remove item        |

### Bill of Materials

| Method    | Endpoint                                 | Description           |
| --------- | ---------------------------------------- | --------------------- |
| GET       | `/api/products/bom/`                     | List BOMs             |
| POST      | `/api/products/bom/`                     | Create BOM            |
| GET       | `/api/products/bom/{id}/`                | BOM detail            |
| PUT/PATCH | `/api/products/bom/{id}/`                | Update BOM            |
| DELETE    | `/api/products/bom/{id}/`                | Delete BOM            |
| GET       | `/api/products/bom/{id}/cost_breakdown/` | Cost calculation      |
| GET       | `/api/products/bom/{id}/stock_check/`    | Material availability |

### BOM Items

| Method    | Endpoint                        | Description    |
| --------- | ------------------------------- | -------------- |
| GET       | `/api/products/bom-items/`      | List BOM items |
| POST      | `/api/products/bom-items/`      | Add BOM item   |
| PUT/PATCH | `/api/products/bom-items/{id}/` | Update item    |
| DELETE    | `/api/products/bom-items/{id}/` | Remove item    |

---

## Services Reference

| Service                     | Method                           | Returns        |
| --------------------------- | -------------------------------- | -------------- |
| `BundleStockService`        | `get_available_stock()`          | `int`          |
|                             | `check_availability(qty)`        | `bool`         |
|                             | `get_limiting_item()`            | `dict \| None` |
|                             | `reserve_stock(qty)`             | `bool`         |
| `BundlePricingService`      | `get_bundle_price()`             | `Decimal`      |
|                             | `get_individual_total()`         | `Decimal`      |
|                             | `get_savings()`                  | `Decimal`      |
|                             | `calculate_fixed_price()`        | `Decimal`      |
|                             | `calculate_dynamic_price()`      | `Decimal`      |
| `CostCalculationService`    | `calculate_material_cost()`      | `Decimal`      |
|                             | `calculate_with_wastage()`       | `Decimal`      |
|                             | `calculate_labor_cost()`         | `Decimal`      |
|                             | `calculate_overhead()`           | `Decimal`      |
|                             | `calculate_total_cost()`         | `Decimal`      |
|                             | `calculate_unit_cost()`          | `Decimal`      |
|                             | `suggest_selling_price(margin%)` | `dict`         |
| `ManufacturingStockService` | `check_raw_materials()`          | `list[dict]`   |
|                             | `get_producible_quantity()`      | `int`          |

---

## Sri Lanka Business Examples

### Tea Gift Set (Bundle)

```
Ceylon Tea Gift Set (DYNAMIC, 15% discount):
  - Ceylon Black Tea 100g × 2  @ Rs. 450.00
  - Silver Tea Strainer × 1   @ Rs. 1200.00
  - Gift Box Wooden × 1       @ Rs. 350.00 (optional)
  ─────────────────────────
  Component Total: Rs. 2100.00
  After 15% discount: Rs. 1785.00
  Savings: Rs. 315.00
```

### Spice Mix (Composite / BOM)

```
Sri Lankan Curry Powder (yield: 50 × 100g packets):
  - Coriander Seeds 2kg  @ Rs. 800/kg  (5% wastage)
  - Cumin Seeds 1kg      @ Rs. 1500/kg (3% wastage)
  - Chili Flakes 0.5kg   @ Rs. 2000/kg (2% wastage)
  - Turmeric 0.3kg       @ Rs. 900/kg  (0% wastage)
  ─────────────────────────
  Material Cost: Rs. 4570.00
  With Wastage:  Rs. 4704.50
  Labor:         Rs. 500.00
  Overhead (10%): Rs. 520.45
  Total:         Rs. 5724.95
  Unit Cost:     Rs. 114.50
  Selling Price: Rs. 148.85 (30% margin)
```

---

## Testing

```bash
# Run bundle tests
docker compose run --rm --entrypoint "" backend bash -c \
  "pip install -q pytest pytest-django && python -m pytest tests/products/test_bundle_models.py -v"

# Run BOM tests
docker compose run --rm --entrypoint "" backend bash -c \
  "pip install -q pytest pytest-django && python -m pytest tests/products/test_bom_models.py -v"

# Run integration tests
docker compose run --rm --entrypoint "" backend bash -c \
  "pip install -q pytest pytest-django && python -m pytest tests/products/test_sp05_integration.py -v"
```
