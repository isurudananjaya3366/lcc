# Product Variants — SP04 Implementation Guide

## Overview

SP04 implements a full product variant system for the POS/ERP platform,
enabling VARIABLE-type products to have configurable option types (e.g.
Size, Color) with values, and automatically generated variant
combinations.

---

## Architecture

### Models

| Model                  | Table                           | Description                                                                 |
| ---------------------- | ------------------------------- | --------------------------------------------------------------------------- |
| `VariantOptionType`    | `products_variantoptiontype`    | Option category (e.g. Size, Color). Supports color and image swatches.      |
| `VariantOptionValue`   | `products_variantoptionvalue`   | A specific value within a type (e.g. S, M, L for Size).                     |
| `ProductVariant`       | `products_productvariant`       | A purchasable variant of a VARIABLE product (e.g. "T-Shirt - Small / Red"). |
| `ProductVariantOption` | `products_productvariantoption` | Through model linking a variant to its option values.                       |
| `ProductOptionConfig`  | `products_productoptionconfig`  | Links a product to its applicable option types.                             |

### Relationships

```
Product (VARIABLE)
  ├── ProductOptionConfig ──→ VariantOptionType
  │                              └── VariantOptionValue (1..N)
  └── ProductVariant (1..N)
        └── ProductVariantOption ──→ VariantOptionValue
```

### Managers & QuerySets

- `VariantManager` on `ProductVariant.objects` provides chainable
  filters and the `get_by_options()` lookup method.
- `VariantQuerySet` methods: `active()`, `inactive()`, `in_stock()`,
  `for_product()`, `by_option()`, `with_prices()`, `with_stock()`,
  `with_options()`.

### Services

- **VariantGenerator** (`apps.products.services.VariantGenerator`):
  Generates all Cartesian combinations of option values for a product,
  creates unique SKUs, and bulk-creates variants with through-model
  links.
- **Config** (`apps.products.services.config`): SKU pattern defaults,
  separator, max retry, validation and formatting utilities.

### Signals

- `auto_generate_variant_name` (pre_save): Auto-generates variant
  names from linked option values.
- `variant_post_save_handler` (post_save): Logs variant
  creation/update events.

---

## API Endpoints

All endpoints require authentication (`IsAuthenticated`).

### Variant Option Types

| Method    | Endpoint                                   | Description           |
| --------- | ------------------------------------------ | --------------------- |
| GET       | `/api/products/variant-option-types/`      | List all option types |
| POST      | `/api/products/variant-option-types/`      | Create option type    |
| GET       | `/api/products/variant-option-types/{id}/` | Retrieve option type  |
| PUT/PATCH | `/api/products/variant-option-types/{id}/` | Update option type    |
| DELETE    | `/api/products/variant-option-types/{id}/` | Delete option type    |

**Filters**: `is_active`, `is_color_swatch`, `is_image_swatch`
**Search**: `name`
**Ordering**: `name`, `display_order`, `created_on`

### Variant Option Values

| Method    | Endpoint                                              | Description         |
| --------- | ----------------------------------------------------- | ------------------- |
| GET       | `/api/products/variant-option-values/`                | List all values     |
| POST      | `/api/products/variant-option-values/`                | Create value        |
| GET       | `/api/products/variant-option-values/{id}/`           | Retrieve value      |
| PUT/PATCH | `/api/products/variant-option-values/{id}/`           | Update value        |
| DELETE    | `/api/products/variant-option-values/{id}/`           | Delete value        |
| GET       | `/api/products/variant-option-values/by-type/{slug}/` | Values by type slug |

**Filters**: `option_type`, `is_active`
**Search**: `value`, `label`

### Product Variants

| Method    | Endpoint                                     | Description              |
| --------- | -------------------------------------------- | ------------------------ |
| GET       | `/api/products/product-variants/`            | List variants            |
| POST      | `/api/products/product-variants/`            | Create variant           |
| GET       | `/api/products/product-variants/{id}/`       | Retrieve variant detail  |
| PUT/PATCH | `/api/products/product-variants/{id}/`       | Update variant           |
| DELETE    | `/api/products/product-variants/{id}/`       | Delete variant           |
| GET       | `/api/products/product-variants/by-options/` | Lookup by exact options  |
| POST      | `/api/products/product-variants/generate/`   | Bulk-generate all combos |

**by-options query params**: `product_id` (UUID), `option_values` (comma-separated UUIDs)
**generate body**: `{ "product_id": "<UUID>" }`

**Filters**: `product`, `is_active`
**Search**: `sku`, `name`, `barcode`
**Ordering**: `sku`, `name`, `sort_order`, `created_on`

### Product Option Configs

| Method    | Endpoint                                     | Description     |
| --------- | -------------------------------------------- | --------------- |
| GET       | `/api/products/product-option-configs/`      | List configs    |
| POST      | `/api/products/product-option-configs/`      | Create config   |
| GET       | `/api/products/product-option-configs/{id}/` | Retrieve config |
| PUT/PATCH | `/api/products/product-option-configs/{id}/` | Update config   |
| DELETE    | `/api/products/product-option-configs/{id}/` | Delete config   |

**Filters**: `product`, `option_type`, `is_active`

---

## Usage Examples

### Creating Option Types and Values

```python
from apps.products.models import VariantOptionType, VariantOptionValue

size = VariantOptionType.objects.create(name="Size", display_order=1)
VariantOptionValue.objects.create(option_type=size, value="S", display_order=0)
VariantOptionValue.objects.create(option_type=size, value="M", display_order=1)
VariantOptionValue.objects.create(option_type=size, value="L", display_order=2)

color = VariantOptionType.objects.create(
    name="Color", display_order=2, is_color_swatch=True
)
VariantOptionValue.objects.create(
    option_type=color, value="Red", color_code="#FF0000", display_order=0
)
VariantOptionValue.objects.create(
    option_type=color, value="Blue", color_code="#0000FF", display_order=1
)
```

### Configuring a Product

```python
from apps.products.models import Product, ProductOptionConfig
from apps.products.constants import PRODUCT_TYPES

product = Product.objects.create(
    name="Classic T-Shirt",
    product_type=PRODUCT_TYPES.VARIABLE,
    selling_price=2500,
)
ProductOptionConfig.objects.create(product=product, option_type=size, display_order=0)
ProductOptionConfig.objects.create(product=product, option_type=color, display_order=1)
```

### Generating Variants

```python
from apps.products.services import VariantGenerator

generator = VariantGenerator(product)
is_valid, error = generator.validate_combinations()
if is_valid:
    variants = generator.generate_variants()
    # Creates 6 variants: S/Red, S/Blue, M/Red, M/Blue, L/Red, L/Blue
```

### Querying Variants

```python
from apps.products.models import ProductVariant

# Active variants for a product
ProductVariant.objects.active().for_product(product)

# Filter by option value
ProductVariant.objects.by_option(size_medium)

# AND logic with multiple options
ProductVariant.objects.by_option([size_medium, color_red])

# Exact match lookup
variant = ProductVariant.objects.get_by_options(
    product, {"Size": "M", "Color": "Red"}
)

# Prefetch for display
ProductVariant.objects.for_product(product).with_options()
```

---

## Admin Integration

- **VariantOptionTypeAdmin**: Inline values, search by name
- **ProductVariantAdmin**: Inline option links, search by SKU/name
- **ProductOptionConfigAdmin**: Product-type config management
- **ProductAdmin**: Includes collapsible `ProductVariantTabInline`

---

## Files

| Path                                      | Description                                               |
| ----------------------------------------- | --------------------------------------------------------- |
| `models/variant_option.py`                | VariantOptionType, VariantOptionValue                     |
| `models/product_variant.py`               | ProductVariant, ProductVariantOption, ProductOptionConfig |
| `models/variant_managers.py`              | VariantQuerySet, VariantManager                           |
| `services/config.py`                      | SKU configuration utilities                               |
| `services/variant_generator.py`           | VariantGenerator bulk creation                            |
| `signals.py`                              | Auto-name generation, post-save logging                   |
| `api/serializers.py`                      | 8 variant serializers                                     |
| `api/views.py`                            | 4 variant ViewSets                                        |
| `api/urls.py`                             | URL routing (4 new endpoints)                             |
| `admin.py`                                | Admin classes and inlines                                 |
| `migrations/0006_sp04_variant_options.py` | VariantOptionType/Value                                   |
| `migrations/0007_sp04_product_variant.py` | ProductVariant/Option/Config                              |

---

## Test Coverage

| Test File                   | Count   | Scope                           |
| --------------------------- | ------- | ------------------------------- |
| `test_variant_option.py`    | 35      | VariantOptionType/Value models  |
| `test_variant_managers.py`  | 37      | VariantQuerySet, VariantManager |
| `test_variant_models.py`    | 30      | ProductVariant, Option, Config  |
| `test_variant_generator.py` | 27      | VariantGenerator service        |
| `test_variant_api.py`       | 60      | Serializers, Views, URLs        |
| **Total**                   | **189** |                                 |

---

## Future Enhancements (Placeholders)

- `VariantQuerySet.in_stock()` — currently returns `active()`;
  will integrate with `VariantStock` model (Phase-05).
- `VariantQuerySet.with_prices()` / `with_stock()` — prefetch
  placeholders for `VariantPrice` / `VariantStock` models.
