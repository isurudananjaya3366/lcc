# Category Module — Overview

## Architecture

The Category module provides **hierarchical product categorization** for the LankaCommerce Cloud POS system using [django-mptt](https://django-mptt.readthedocs.io/) (Modified Preorder Tree Traversal).

### Key design choices

| Concern              | Approach                                                                                                                                                          |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Tree storage**     | MPTT nested-set model — four auto-managed integer columns (`lft`, `rght`, `tree_id`, `level`) enable efficient ancestor/descendant queries without recursive SQL. |
| **Tenant isolation** | django-tenants schema isolation. Each tenant has its own `products_category` table in a dedicated PostgreSQL schema; slug uniqueness is per-schema.               |
| **Identity**         | UUID primary key via `UUIDMixin`.                                                                                                                                 |
| **Timestamps**       | `created_on` / `updated_on` via `TimestampMixin`.                                                                                                                 |
| **Ordering**         | `order_insertion_by = ["display_order", "name"]` — MPTT inserts children in display-order, then alphabetically.                                                   |

### Component map

```
apps/products/
├── models/
│   ├── category.py          # Category MPTTModel
│   └── managers.py          # CategoryManager, CategoryQuerySet
├── api/
│   ├── serializers.py       # List / Detail / Tree / CreateUpdate serializers
│   ├── views.py             # CategoryViewSet (ModelViewSet + tree/move actions)
│   └── urls.py              # DRF router  →  /api/v1/categories/
├── admin.py                 # MPTTModelAdmin with drag-drop
├── management/commands/
│   ├── seed_categories.py   # Seed sample Sri Lankan categories
│   ├── rebuild_tree.py      # Rebuild lft/rght/tree_id/level
│   ├── export_categories.py # Export to JSON
│   └── import_categories.py # Import from JSON
└── docs/                    # You are here
```

---

## Model Fields Reference

### Core fields

| Field             | Type                   | Constraints             | Description                                                   |
| ----------------- | ---------------------- | ----------------------- | ------------------------------------------------------------- |
| `id`              | `UUIDField`            | PK, auto                | Unique identifier (from `UUIDMixin`).                         |
| `name`            | `CharField(255)`       | indexed                 | Display name.                                                 |
| `slug`            | `SlugField(255)`       | unique (per schema)     | URL-friendly identifier. Auto-generated from `name` if blank. |
| `description`     | `TextField`            | blank, default `""`     | Optional rich-text description.                               |
| `parent`          | `TreeForeignKey(self)` | null, blank, CASCADE    | Parent category. `None` = root node.                          |
| `image`           | `ImageField`           | null, blank             | Upload path: `categories/<slug>/<filename>`.                  |
| `icon`            | `CharField(100)`       | blank, default `""`     | CSS icon class (e.g. `fas fa-mobile-alt`).                    |
| `is_active`       | `BooleanField`         | default `True`, indexed | Controls storefront visibility.                               |
| `display_order`   | `PositiveIntegerField` | default `0`             | Sort weight within a level; lower = first.                    |
| `seo_title`       | `CharField(100)`       | blank                   | `<title>` tag for SEO (60 chars optimal).                     |
| `seo_description` | `CharField(200)`       | blank                   | Meta description (155 chars optimal).                         |
| `seo_keywords`    | `CharField(255)`       | blank                   | Comma-separated keywords (legacy SEO).                        |

### Timestamp fields (from `TimestampMixin`)

| Field        | Type            | Description            |
| ------------ | --------------- | ---------------------- |
| `created_on` | `DateTimeField` | Set on creation.       |
| `updated_on` | `DateTimeField` | Updated on every save. |

### MPTT auto-managed fields (do **not** set manually)

| Field     | Description                           |
| --------- | ------------------------------------- |
| `tree_id` | Groups all nodes in the same tree.    |
| `lft`     | Left value for nested-set traversal.  |
| `rght`    | Right value for nested-set traversal. |
| `level`   | Depth in the tree (`0` = root).       |

### Database indexes

| Name                        | Fields                       |
| --------------------------- | ---------------------------- |
| `idx_category_active_order` | `is_active`, `display_order` |
| `idx_category_tree_lft`     | `tree_id`, `lft`             |
| `idx_category_slug`         | `slug`                       |

---

## Manager & QuerySet API

### `CategoryQuerySet` (extends `TreeQuerySet`)

| Method             | Returns            | Description                             |
| ------------------ | ------------------ | --------------------------------------- |
| `.active()`        | `CategoryQuerySet` | `is_active=True`                        |
| `.inactive()`      | `CategoryQuerySet` | `is_active=False`                       |
| `.root_nodes()`    | `CategoryQuerySet` | Root categories (`parent__isnull=True`) |
| `.with_children()` | `CategoryQuerySet` | Prefetch direct `children` (avoids N+1) |
| `.with_products()` | `CategoryQuerySet` | Prefetch reverse `products` relation    |

All methods are chainable:

```python
Category.objects.active().root_nodes().with_children()
```

### `CategoryManager` (extends `TreeManager`)

| Method                  | Signature                                   | Description                                                                                         |
| ----------------------- | ------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `get_tree()`            | `(active_only=True)`                        | Returns root nodes with children prefetched. When `active_only=True`, filters to active categories. |
| `get_breadcrumbs()`     | `(category, include_self=True)`             | Returns ancestor chain root → current.                                                              |
| `get_descendants_ids()` | `(category, include_self=True)`             | Flat `list[UUID]` of descendant IDs — useful for product filtering.                                 |
| `move_node()`           | `(category, target, position='last-child')` | Move a node; raises `ValueError` on cycle.                                                          |

---

## Tree Structure

MPTT stores categories as a **nested set**. Each node has `lft` and `rght` values such that a node contains all nodes with `lft` between its own `lft` and `rght`.

```
Electronics (lft=1, rght=12, level=0)
├── Mobile Phones (lft=2, rght=7, level=1)
│   ├── Smartphones (lft=3, rght=4, level=2)
│   └── Feature Phones (lft=5, rght=6, level=2)
└── Accessories (lft=8, rght=11, level=1)
    ├── Chargers (lft=9, rght=10, level=2)
```

### Efficient queries provided by MPTT

| Operation       | MPTT method              | SQL cost                   |
| --------------- | ------------------------ | -------------------------- |
| Get ancestors   | `node.get_ancestors()`   | Single query               |
| Get descendants | `node.get_descendants()` | Single query               |
| Get children    | `node.get_children()`    | Single query               |
| Get siblings    | `node.get_siblings()`    | Single query               |
| Check leaf      | `node.is_leaf_node()`    | Computed from `lft`/`rght` |
| Check root      | `node.is_root_node()`    | `level == 0`               |

---

## Usage Examples

### Creating categories

```python
from apps.products.models import Category

# Root category
electronics = Category.objects.create(
    name="Electronics",
    slug="electronics",
    icon="fas fa-tv",
)

# Child category
phones = Category.objects.create(
    name="Mobile Phones",
    slug="mobile-phones",
    parent=electronics,
    icon="fas fa-mobile-alt",
)

# Deeper nesting
smartphones = Category.objects.create(
    name="Smartphones",
    slug="smartphones",
    parent=phones,
)
```

### Querying the tree

```python
# Full tree of active roots with children prefetched
tree = Category.objects.get_tree(active_only=True)

# Breadcrumbs for a detail page
crumbs = Category.objects.get_breadcrumbs(smartphones)
# QuerySet: [Electronics, Mobile Phones, Smartphones]

# All category IDs under Electronics (for product filtering)
ids = Category.objects.get_descendants_ids(electronics)
Product.objects.filter(category_id__in=ids)

# Full path string
smartphones.get_full_path()  # "Electronics > Mobile Phones > Smartphones"

# Direct children
electronics.get_children()

# Leaf check
smartphones.is_leaf   # True
electronics.is_leaf   # False
```

### Moving nodes

```python
# Move "Smartphones" to become a direct child of "Electronics"
Category.objects.move_node(
    smartphones, electronics, position="first-child"
)

# Make a category a new root
Category.objects.move_node(phones, target=None)
```

### QuerySet chaining

```python
# Active root categories with children prefetched
roots = Category.objects.active().root_nodes().with_children()

# Inactive categories
Category.objects.inactive()

# Categories with products prefetched
Category.objects.active().with_products()
```
