# Products App

Multi-tenant product catalog for the **LankaCommerce Cloud POS** system.

Includes hierarchical categories (django-mptt), brands, tax classes, units of measure, and a
full-featured Product model with auto-generated SKU/slug, PostgreSQL full-text search,
pricing, SEO fields, and dual-channel visibility (webstore + POS).

---

## Overview

| Module            | Description                                          |
| ----------------- | ---------------------------------------------------- |
| **Category**      | MPTT tree with unlimited nesting, drag-drop admin    |
| **Brand**         | Product brands with auto-slugs and logo support      |
| **TaxClass**      | Tax rates with single-default enforcement per tenant |
| **UnitOfMeasure** | Base/derived units with conversion factors           |
| **Product**       | Core product model — 27+ fields, 4 types, 4 statuses |

### Key capabilities

- **Tenant isolation** — django-tenants schema separation; each tenant has independent data
- **UUID primary keys** — safe cross-system references
- **Auto SKU generation** — `PRD-{category_code}-{uuid_segment}` format
- **Auto slug generation** — from product name, unique per tenant
- **PostgreSQL full-text search** — weighted SearchVector on name, description, SKU, barcode
- **Product types** — Simple, Variable, Bundle, Composite
- **Product statuses** — Draft, Active, Archived, Discontinued
- **Dual visibility** — separate webstore and POS toggles with `db_index`
- **Pricing** — cost, selling, MRP, wholesale with profit margin calculation
- **SEO** — title (100 chars) and description (300 chars) per product
- **Soft delete** — `is_deleted` + `deleted_on` with restore support

---

## Quick Start

### 1. Seed sample categories

```bash
python manage.py seed_categories
```

### 2. Verify via API

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/products/
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/brands/
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/tax-classes/
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/categories/tree/
```

### 3. Access the admin

Navigate to `/admin/products/` for the admin interface.

---

## API Endpoints

### Categories

| Method   | Endpoint                        | Description                              |
| -------- | ------------------------------- | ---------------------------------------- |
| `GET`    | `/api/v1/categories/`           | List categories (filterable, searchable) |
| `POST`   | `/api/v1/categories/`           | Create a category                        |
| `GET`    | `/api/v1/categories/{id}/`      | Retrieve category detail                 |
| `PUT`    | `/api/v1/categories/{id}/`      | Full update                              |
| `PATCH`  | `/api/v1/categories/{id}/`      | Partial update                           |
| `DELETE` | `/api/v1/categories/{id}/`      | Delete (cascades children)               |
| `GET`    | `/api/v1/categories/tree/`      | Full recursive tree                      |
| `POST`   | `/api/v1/categories/{id}/move/` | Move node in tree                        |

### Brands

| Method   | Endpoint               | Description                         |
| -------- | ---------------------- | ----------------------------------- |
| `GET`    | `/api/v1/brands/`      | List brands (search, filter active) |
| `POST`   | `/api/v1/brands/`      | Create a brand                      |
| `GET`    | `/api/v1/brands/{id}/` | Retrieve brand detail               |
| `PUT`    | `/api/v1/brands/{id}/` | Full update                         |
| `PATCH`  | `/api/v1/brands/{id}/` | Partial update                      |
| `DELETE` | `/api/v1/brands/{id}/` | Delete                              |

### Tax Classes

| Method   | Endpoint                    | Description                          |
| -------- | --------------------------- | ------------------------------------ |
| `GET`    | `/api/v1/tax-classes/`      | List tax classes (filter by default) |
| `POST`   | `/api/v1/tax-classes/`      | Create a tax class                   |
| `GET`    | `/api/v1/tax-classes/{id}/` | Retrieve tax class detail            |
| `PUT`    | `/api/v1/tax-classes/{id}/` | Full update                          |
| `PATCH`  | `/api/v1/tax-classes/{id}/` | Partial update                       |
| `DELETE` | `/api/v1/tax-classes/{id}/` | Delete                               |

### Products

| Method   | Endpoint                      | Description                                 |
| -------- | ----------------------------- | ------------------------------------------- |
| `GET`    | `/api/v1/products/`           | List products (filter, search, paginate)    |
| `POST`   | `/api/v1/products/`           | Create product (auto SKU/slug generation)   |
| `GET`    | `/api/v1/products/{id}/`      | Retrieve product detail (nested serializer) |
| `PUT`    | `/api/v1/products/{id}/`      | Full update                                 |
| `PATCH`  | `/api/v1/products/{id}/`      | Partial update                              |
| `DELETE` | `/api/v1/products/{id}/`      | Delete                                      |
| `GET`    | `/api/v1/products/published/` | Active + webstore-visible products          |
| `GET`    | `/api/v1/products/featured/`  | Active + featured products                  |

**Product query parameters:** `?category=`, `?brand=`, `?product_type=`, `?status=`, `?featured=`,
`?is_webstore_visible=`, `?is_pos_visible=`, `?min_price=`, `?max_price=`, `?search=`, `?ordering=`

---

## Model Reference

### Product

The core product model with 27+ fields supporting 4 product types (Simple, Variable, Bundle, Composite) and 4 statuses (Draft, Active, Archived, Discontinued).

| Field                              | Type                   | Description                        |
| ---------------------------------- | ---------------------- | ---------------------------------- |
| `name`                             | `CharField(255)`       | Display name                       |
| `slug`                             | `SlugField(255)`       | Unique per tenant, auto-generated  |
| `sku`                              | `CharField(50)`        | Stock Keeping Unit, auto-generated |
| `barcode`                          | `CharField(50)`        | Optional barcode (EAN/UPC)         |
| `description`                      | `TextField`            | Full description                   |
| `short_description`                | `CharField(500)`       | Brief summary                      |
| `category`                         | `ForeignKey(Category)` | Required, PROTECT on delete        |
| `brand`                            | `ForeignKey(Brand)`    | Optional, SET_NULL on delete       |
| `product_type`                     | `CharField(20)`        | simple/variable/bundle/composite   |
| `status`                           | `CharField(15)`        | draft/active/archived/discontinued |
| `tax_class`                        | `ForeignKey(TaxClass)` | Optional, SET_NULL on delete       |
| `unit_of_measure`                  | `ForeignKey(UOM)`      | Optional, SET_NULL on delete       |
| `cost_price`                       | `DecimalField(12,2)`   | Purchase cost                      |
| `selling_price`                    | `DecimalField(12,2)`   | Customer selling price             |
| `mrp`                              | `DecimalField(12,2)`   | Maximum retail price               |
| `wholesale_price`                  | `DecimalField(12,2)`   | Wholesale/bulk price               |
| `weight`/`length`/`width`/`height` | `DecimalField`         | Physical dimensions                |
| `seo_title`                        | `CharField(100)`       | Meta title for SEO                 |
| `seo_description`                  | `CharField(300)`       | Meta description for SEO           |
| `is_webstore_visible`              | `BooleanField`         | Webstore display toggle (indexed)  |
| `is_pos_visible`                   | `BooleanField`         | POS display toggle (indexed)       |
| `featured`                         | `BooleanField`         | Featured product flag              |

**Auto-generated fields:** `slug` (from name), `sku` (PRD-{category}-{uuid})

**Properties:** `profit_margin` — calculates `(selling - cost) / cost * 100`

### Brand

| Field         | Type             | Description              |
| ------------- | ---------------- | ------------------------ |
| `name`        | `CharField(255)` | Brand name               |
| `slug`        | `SlugField(255)` | Auto-generated from name |
| `description` | `TextField`      | Optional description     |
| `website`     | `URLField`       | Brand website            |
| `logo`        | `ImageField`     | Brand logo               |

### TaxClass

| Field         | Type                | Description                               |
| ------------- | ------------------- | ----------------------------------------- |
| `name`        | `CharField(100)`    | Tax class name                            |
| `rate`        | `DecimalField(5,2)` | Tax rate percentage                       |
| `is_default`  | `BooleanField`      | Single default per tenant (auto-enforced) |
| `description` | `TextField`         | Optional description                      |

### UnitOfMeasure

| Field               | Type                 | Description                  |
| ------------------- | -------------------- | ---------------------------- |
| `name`              | `CharField(100)`     | Unit name                    |
| `symbol`            | `CharField(10)`      | Short symbol (kg, pcs, etc.) |
| `is_base_unit`      | `BooleanField`       | Whether this is a base unit  |
| `conversion_factor` | `DecimalField(10,4)` | Conversion to base unit      |
| `description`       | `TextField`          | Optional description         |

### Category (MPTT)

| Field             | Type                   | Description                       |
| ----------------- | ---------------------- | --------------------------------- |
| `name`            | `CharField(255)`       | Display name                      |
| `slug`            | `SlugField(255)`       | Unique per tenant, auto-generated |
| `parent`          | `TreeForeignKey`       | Parent category (`null` = root)   |
| `description`     | `TextField`            | Optional description              |
| `image`           | `ImageField`           | Category image                    |
| `icon`            | `CharField(100)`       | CSS icon class                    |
| `is_active`       | `BooleanField`         | Storefront visibility             |
| `display_order`   | `PositiveIntegerField` | Sort weight (lower = first)       |
| `seo_title`       | `CharField(100)`       | Meta title                        |
| `seo_description` | `CharField(200)`       | Meta description                  |
| `seo_keywords`    | `CharField(255)`       | Comma-separated keywords          |

### MPTT fields (auto-managed)

`tree_id`, `lft`, `rght`, `level` — do **not** set manually.

---

## QuerySet & Manager API

### ProductQuerySet methods (chainable)

| Method                | Returns                             |
| --------------------- | ----------------------------------- |
| `active()`            | Active, non-deleted products        |
| `published()`         | Active + webstore visible           |
| `in_stock()`          | Placeholder (returns active)        |
| `by_category(cat)`    | Filter by category (object or UUID) |
| `by_brand(brand)`     | Filter by brand (object or UUID)    |
| `by_status(status)`   | Filter by status choice             |
| `simple_products()`   | Simple type only                    |
| `variable_products()` | Variable type only                  |
| `featured()`          | Featured products only              |
| `for_pos()`           | Active + POS visible                |
| `for_webstore()`      | Active + webstore visible           |

### ProductManager methods

| Method           | Description                                         |
| ---------------- | --------------------------------------------------- |
| `search(query)`  | PostgreSQL full-text search with icontains fallback |
| `active()`       | Proxy to QuerySet.active()                          |
| `published()`    | Proxy to QuerySet.published()                       |
| `for_pos()`      | Proxy to QuerySet.for_pos()                         |
| `for_webstore()` | Proxy to QuerySet.for_webstore()                    |

### Model properties

| Property / Method    | Returns   | Description       |
| -------------------- | --------- | ----------------- |
| `profit_margin`      | `Decimal` | Profit margin %   |
| `is_root` (Category) | `bool`    | Root node check   |
| `is_leaf` (Category) | `bool`    | Leaf node check   |
| `get_full_path(sep)` | `str`     | Breadcrumb string |

See [docs/overview.md](docs/overview.md) for additional details.

---

## Management Commands

### `seed_categories`

Populate the database with sample hierarchical categories.

```bash
python manage.py seed_categories          # Create sample tree
python manage.py seed_categories --clear  # Clear existing then seed
```

### `rebuild_tree`

Recalculate MPTT fields (`lft`, `rght`, `tree_id`, `level`). Use after bulk SQL operations or when the tree appears corrupted.

```bash
python manage.py rebuild_tree
```

### `export_categories`

Export categories as JSON for backup or transfer.

```bash
python manage.py export_categories                         # stdout
python manage.py export_categories --output=cats.json      # file
python manage.py export_categories --active-only --indent=4
```

### `import_categories`

Import categories from a JSON file (format matching `export_categories` output).

```bash
python manage.py import_categories --input=cats.json
python manage.py import_categories --input=cats.json --clear  # clear first
```

---

## Testing

Comprehensive test suite using real PostgreSQL with tenant schema isolation.

| Suite               | Location                                     | Description                     |
| ------------------- | -------------------------------------------- | ------------------------------- |
| Category Models     | `tests/products/test_models.py`              | 151 tests — MPTT, CRUD, tree    |
| Category API        | `tests/products/test_api.py`                 | 120 tests — endpoints, serial.  |
| Product Models      | `tests/products/test_product_models.py`      | 263 tests — fields, manager, QS |
| Product API (unit)  | `tests/products/test_product_api.py`         | 143 tests — serializer, filter  |
| Product Integration | `tests/products/test_product_integration.py` | 110+ tests — CRUD, API, tenant  |

### Running tests

```bash
# All products tests
DJANGO_SETTINGS_MODULE=config.settings.test_pg pytest tests/products/ -v

# Only product model tests
pytest tests/products/test_product_models.py -v

# Only integration tests
pytest tests/products/test_product_integration.py -v

# With coverage
pytest tests/products/ --cov=apps.products --cov-report=term-missing
```

---

## Troubleshooting

### Tree corruption

**Symptoms:** Categories display in wrong order, `get_ancestors()` returns unexpected results, missing nodes in tree view.

**Cause:** Direct SQL updates, failed migrations, or interrupted bulk operations can corrupt MPTT's `lft`/`rght`/`tree_id`/`level` fields.

**Fix:**

```bash
python manage.py rebuild_tree
```

This recalculates all MPTT fields from the `parent` foreign-key relationships.

### Slug conflicts

**Symptoms:** `IntegrityError` on category creation with duplicate slug.

**Cause:** Slugs are unique per tenant schema. Two categories with the same name will collide.

**Fix:** The `CategoryCreateUpdateSerializer` auto-generates unique slugs by appending a numeric suffix (`electronics`, `electronics-2`, `electronics-3`). If creating categories directly via the ORM, either provide a unique slug or let the model's `save()` method auto-slugify.

### Cycle detection

**Symptoms:** `ValueError: Cannot move a category to its own descendant.`

**Cause:** Attempting to move a parent node under one of its own children (which would create an infinite loop).

**Fix:** This is expected — the move is rejected. Choose a different target.

### N+1 query issues

Use the provided QuerySet methods to prefetch related data:

```python
Category.objects.active().root_nodes().with_children()  # prefetch children
Category.objects.active().with_products()                # prefetch products
```

---

## Sri Lankan Context Examples

The seed data includes category hierarchies relevant to Sri Lankan retail:

```
Electronics
├── Mobile Phones
│   ├── Smartphones
│   └── Feature Phones
├── Laptops & Computers
│   ├── Gaming Laptops
│   └── Business Laptops
├── Accessories
│   ├── Chargers & Cables
│   └── Cases & Covers
└── Home Appliances

Clothing
├── Men's Wear
├── Women's Wear
└── Children's Wear

Groceries
├── Rice & Grains
├── Spices & Condiments
└── Beverages
```

These categories reflect common product structures for Sri Lankan retailers using the POS system, covering electronics shops, clothing stores, and grocery outlets.
