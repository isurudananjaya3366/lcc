# POS Product Search

## Overview

`ProductSearchService` provides a unified, stateless search interface for POS
terminals. All methods are `@classmethod` and return plain dictionaries
(not Django model instances) for easy serialization.

## Search Methods

### 1. Barcode Search

```python
ProductSearchService.barcode_search(barcode: str) -> dict | None
```

- Strips whitespace then searches:
  1. **Weight-embedded barcode** — detects prefix, extracts product code
     and weight, looks up by truncated barcode.
  2. **Variant barcode** — exact match on `ProductVariant.barcode`.
  3. **Product barcode** — exact match on `Product.barcode`.
- Returns a single result dict or `None`.

### 2. SKU Search

```python
ProductSearchService.sku_search(sku: str, exact: bool = True) -> list[dict]
```

- `exact=True` — case-insensitive exact match (`iexact`).
- `exact=False` — starts-with match (`istartswith`).
- Searches both `Product.sku` and `ProductVariant.sku`.

### 3. Name Search

```python
ProductSearchService.name_search(query: str, limit: int = 20) -> list[dict]
```

- Minimum 2 characters.
- Uses `icontains` on `Product.name`.
- Results capped at `limit`.

### 4. Combined Search

```python
ProductSearchService.combined_search(query: str, limit: int = 20) -> list[dict]
```

Priority cascade:

1. **Barcode match** → if found, return immediately.
2. **Exact SKU match** → if found, return immediately.
3. **Name search + partial SKU** → merge, deduplicate, cap to `limit`.

## Result Format

Every method returns dicts with:

```json
{
  "id": "uuid",
  "name": "Coca Cola 330ml",
  "sku": "COKE-330",
  "barcode": "8901234567890",
  "selling_price": "150.00",
  "cost_price": "80.00",
  "category": "Beverages",
  "brand": "Coca-Cola",
  "tax_class": "Standard",
  "product_type": "simple",
  "is_pos_visible": true,
  "search_method": "barcode",
  "variant_id": null,
  "variant_sku": null,
  "variant_barcode": null,
  "variant_name": null
}
```

## Filtering

```python
ProductSearchService.filter_by_category(results: list, category) -> list
```

Filters an existing result list by category (including descendants via
`django-mptt`).

## Search History

```python
ProductSearchService.record_search(
    query_text, result_count, search_method, terminal, user, selected_product=None
)
ProductSearchService.get_recent_searches(terminal, user, limit=10)
ProductSearchService.get_popular_products(terminal, user, limit=10, days=30)
```

- `record_search` stores a `SearchHistory` row.
- `get_recent_searches` returns the most recent searches for a
  user/terminal pair.
- `get_popular_products` aggregates frequently selected products.

## Weight Barcodes

Barcodes beginning with prefix `2` are treated as weight-embedded:

```
2 PPPPP WWWWW C
│ │     │     └─ check digit
│ │     └─────── weight (grams / 10g units)
│ └───────────── product code
└─────────────── prefix
```

The service extracts the product code, looks up the product, and
attaches the parsed weight as the quantity.
