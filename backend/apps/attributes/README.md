# Attributes App

The **attributes** app provides a flexible, type-safe attribute system for enriching products with structured metadata. It supports multiple data types, category-scoped assignments, and faceted filtering for webstore search.

## Overview

Attributes allow merchants to define custom product specifications (e.g., "Color", "Weight", "Screen Size") that can be:

- Organized into **Attribute Groups** (e.g., "Technical Specifications", "Dimensions")
- Assigned to specific **Categories** so only relevant attributes appear on product forms
- Used for **faceted search/filtering** in the webstore
- Included in **product comparison** tables
- Indexed for **full-text search**

## Models

### AttributeGroup

Organizes related attributes into logical groups for display.

| Field           | Type                 | Description                                     |
| --------------- | -------------------- | ----------------------------------------------- |
| `id`            | UUID                 | Primary key (auto-generated)                    |
| `name`          | CharField(100)       | Group name, indexed                             |
| `slug`          | SlugField(100)       | URL-friendly identifier, unique, auto-generated |
| `description`   | TextField            | Optional description                            |
| `display_order` | PositiveIntegerField | Sort order (lower = first), default 0           |
| `is_active`     | BooleanField         | Soft-active flag, default True                  |
| `created_on`    | DateTimeField        | Auto-set on creation                            |
| `updated_on`    | DateTimeField        | Auto-set on save                                |

**Managers:**

- `objects` — `GroupManager` with `.active()` and `.with_attributes()` methods
- `all_with_deleted` — Standard Django manager (includes soft-deleted records)

### Attribute

Defines a product attribute with type-based validation and display settings.

| Field                   | Type                       | Description                                     |
| ----------------------- | -------------------------- | ----------------------------------------------- |
| `id`                    | UUID                       | Primary key (auto-generated)                    |
| `name`                  | CharField(100)             | Attribute name, indexed                         |
| `slug`                  | SlugField(100)             | URL-friendly identifier, unique, auto-generated |
| `group`                 | ForeignKey(AttributeGroup) | Optional group, SET_NULL on delete              |
| `attribute_type`        | CharField(20)              | One of the supported types (see below)          |
| `unit`                  | CharField(20)              | Unit of measure (e.g., "kg", "cm")              |
| `is_required`           | BooleanField               | Whether value is mandatory on products          |
| `is_filterable`         | BooleanField               | Include in webstore faceted filters             |
| `is_searchable`         | BooleanField               | Include values in search index                  |
| `is_comparable`         | BooleanField               | Show in product comparison tables               |
| `is_visible_on_product` | BooleanField               | Display on product detail pages                 |
| `display_order`         | PositiveIntegerField       | Sort order within group                         |
| `validation_regex`      | CharField(255)             | Regex pattern for TEXT validation               |
| `min_value`             | DecimalField(20,4)         | Minimum allowed NUMBER value                    |
| `max_value`             | DecimalField(20,4)         | Maximum allowed NUMBER value                    |
| `categories`            | ManyToManyField(Category)  | Categories this attribute applies to            |

**Managers:**

- `objects` — `AttributeManager` with `.active()`, `.filterable()`, `.searchable()`, `.for_category()`, `.by_type()` methods
- `all_with_deleted` — Standard Django manager

**Validation:**

- `clean()` ensures `min_value <= max_value` when both are set

### AttributeOption

Predefined choices for SELECT and MULTISELECT attributes.

| Field           | Type                  | Description                                 |
| --------------- | --------------------- | ------------------------------------------- |
| `id`            | UUID                  | Primary key (auto-generated)                |
| `attribute`     | ForeignKey(Attribute) | Parent attribute, CASCADE on delete         |
| `value`         | CharField(100)        | Internal value (e.g., "red"), indexed       |
| `label`         | CharField(100)        | Display label (e.g., "Bright Red")          |
| `color_code`    | CharField(7)          | Hex color for swatches (e.g., "#FF0000")    |
| `image`         | ImageField            | Optional thumbnail for visual selection     |
| `display_order` | PositiveIntegerField  | Sort order                                  |
| `is_default`    | BooleanField          | Whether this is the default selected option |

**Managers:**

- `objects` — `OptionManager` with `.for_attribute()`, `.with_images()`, `.defaults()` methods
- `all_with_deleted` — Standard Django manager

**Constraints:**

- `unique_together = [("attribute", "value")]` — No duplicate values per attribute
- `save()` clears other defaults when `is_default=True`

## Attribute Types

| Type             | Constant                      | Use Cases                              |
| ---------------- | ----------------------------- | -------------------------------------- |
| **Text**         | `TEXT = "text"`               | Brand name, material, description      |
| **Number**       | `NUMBER = "number"`           | Weight (kg), dimensions (cm), price    |
| **Select**       | `SELECT = "select"`           | Color, size, single-choice dropdowns   |
| **Multi-Select** | `MULTISELECT = "multiselect"` | Features, certifications, multi-choice |
| **Boolean**      | `BOOLEAN = "boolean"`         | Waterproof, organic, wireless          |
| **Date**         | `DATE = "date"`               | Manufacture date, expiry date          |

## Usage Examples

### Creating an Attribute Group

```python
from apps.attributes.models import AttributeGroup

group = AttributeGroup.objects.create(
    name="Technical Specifications",
    description="Hardware and performance specs",
    display_order=1,
)
# slug is auto-generated: "technical-specifications"
```

### Creating Attributes

```python
from apps.attributes.models import Attribute
from apps.attributes.constants import SELECT, NUMBER, BOOLEAN

color = Attribute.objects.create(
    name="Color",
    group=group,
    attribute_type=SELECT,
    is_required=True,
    is_filterable=True,
    is_searchable=True,
    display_order=1,
)

weight = Attribute.objects.create(
    name="Weight",
    group=group,
    attribute_type=NUMBER,
    unit="kg",
    min_value=0,
    max_value=1000,
    display_order=2,
)

waterproof = Attribute.objects.create(
    name="Waterproof",
    attribute_type=BOOLEAN,
    is_filterable=True,
    display_order=3,
)
```

### Creating Options for SELECT/MULTISELECT

```python
from apps.attributes.models import AttributeOption

AttributeOption.objects.create(
    attribute=color,
    value="red",
    label="Bright Red",
    color_code="#FF0000",
    display_order=1,
)

AttributeOption.objects.create(
    attribute=color,
    value="blue",
    label="Ocean Blue",
    color_code="#0066CC",
    display_order=2,
    is_default=True,
)
```

### Assigning Attributes to Categories

```python
from apps.products.models import Category

electronics = Category.objects.get(slug="electronics")
color.categories.add(electronics)
weight.categories.add(electronics)
```

### Querying with Custom Managers

```python
# Get active, filterable attributes
Attribute.objects.active().filter(is_filterable=True)

# Get attributes for a specific category
Attribute.objects.for_category(electronics)

# Get all SELECT-type attributes
Attribute.objects.active().by_type(SELECT)

# Get attribute groups with prefetched attributes
AttributeGroup.objects.active().with_attributes()

# Get default options for an attribute
AttributeOption.objects.for_attribute(color).defaults()
```

## API Endpoints

| Method    | Endpoint                                        | Description                                       |
| --------- | ----------------------------------------------- | ------------------------------------------------- |
| GET       | `/api/attribute-groups/`                        | List all attribute groups                         |
| POST      | `/api/attribute-groups/`                        | Create an attribute group                         |
| GET       | `/api/attribute-groups/{id}/`                   | Retrieve an attribute group                       |
| PUT/PATCH | `/api/attribute-groups/{id}/`                   | Update an attribute group                         |
| DELETE    | `/api/attribute-groups/{id}/`                   | Delete an attribute group                         |
| GET       | `/api/attributes/`                              | List all attributes                               |
| POST      | `/api/attributes/`                              | Create an attribute                               |
| GET       | `/api/attributes/{id}/`                         | Retrieve an attribute (with nested group/options) |
| PUT/PATCH | `/api/attributes/{id}/`                         | Update an attribute                               |
| DELETE    | `/api/attributes/{id}/`                         | Delete an attribute                               |
| GET       | `/api/attributes/by-category/?category_id={id}` | Attributes for a category (with inheritance)      |
| GET       | `/api/attributes/filterable/?category_id={id}`  | Filterable attributes (optional category filter)  |
| GET       | `/api/attribute-options/`                       | List all attribute options                        |
| POST      | `/api/attribute-options/`                       | Create an attribute option                        |
| GET       | `/api/attribute-options/{id}/`                  | Retrieve an attribute option                      |
| PUT/PATCH | `/api/attribute-options/{id}/`                  | Update an attribute option                        |
| DELETE    | `/api/attribute-options/{id}/`                  | Delete an attribute option                        |

All endpoints require authentication (`IsAuthenticated`).

## Multi-Tenant Isolation

This app inherits the project's multi-tenant architecture via `BaseModel`. All queries are automatically scoped to the active tenant through the middleware and database router. Attribute data is isolated per tenant — each tenant defines their own attribute groups, attributes, and options independently.

## Testing

Tests are located in `backend/tests/attributes/` and follow the project convention of **database-free, mock-based testing**:

```bash
# Run all attribute tests
cd backend
python -m pytest tests/attributes/ -v

# Run only model tests
python -m pytest tests/attributes/test_models.py -v

# Run only API tests
python -m pytest tests/attributes/test_api.py -v
```

All tests use `_meta` introspection, `MagicMock`, and `patch` — no database access required.
