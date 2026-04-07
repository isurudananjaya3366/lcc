# Attributes API Documentation

All endpoints require a valid authentication token in the `Authorization` header:

```
Authorization: Token <your-token>
```

---

## Attribute Groups

### List Attribute Groups

```
GET /api/attribute-groups/
```

**Query Parameters:**

| Parameter  | Type   | Description                                                                |
| ---------- | ------ | -------------------------------------------------------------------------- |
| `search`   | string | Search by name or description                                              |
| `ordering` | string | Order by `display_order`, `name`, `created_on` (prefix `-` for descending) |

**Response** `200 OK`:

```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Technical Specifications",
    "slug": "technical-specifications",
    "description": "Hardware and performance specs",
    "display_order": 1,
    "is_active": true,
    "attribute_count": 5,
    "created_on": "2026-01-15T10:30:00Z",
    "updated_on": "2026-01-15T10:30:00Z"
  }
]
```

### Create Attribute Group

```
POST /api/attribute-groups/
```

**Request Body:**

```json
{
  "name": "Dimensions",
  "description": "Physical dimensions and weight",
  "display_order": 2
}
```

**Response** `201 Created`:

```json
{
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "name": "Dimensions",
  "slug": "dimensions",
  "description": "Physical dimensions and weight",
  "display_order": 2,
  "is_active": true,
  "attribute_count": 0,
  "created_on": "2026-01-15T11:00:00Z",
  "updated_on": "2026-01-15T11:00:00Z"
}
```

### Retrieve Attribute Group

```
GET /api/attribute-groups/{id}/
```

**Response** `200 OK`: Same shape as list item.

### Update Attribute Group

```
PUT /api/attribute-groups/{id}/
PATCH /api/attribute-groups/{id}/
```

**Request Body** (PATCH — partial update):

```json
{
  "display_order": 3
}
```

**Response** `200 OK`: Updated group object.

### Delete Attribute Group

```
DELETE /api/attribute-groups/{id}/
```

**Response** `204 No Content`

---

## Attributes

### List Attributes

```
GET /api/attributes/
```

Returns a compact list representation optimized for table/list views.

**Query Parameters:**

| Parameter        | Type    | Description                                                                  |
| ---------------- | ------- | ---------------------------------------------------------------------------- |
| `attribute_type` | string  | Filter by type: `text`, `number`, `select`, `multiselect`, `boolean`, `date` |
| `is_required`    | boolean | Filter by required status                                                    |
| `is_filterable`  | boolean | Filter by filterable status                                                  |
| `group`          | UUID    | Filter by attribute group ID                                                 |
| `search`         | string  | Search by name                                                               |
| `ordering`       | string  | Order by `display_order`, `name`, `created_on`                               |

**Response** `200 OK`:

```json
[
  {
    "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
    "name": "Color",
    "slug": "color",
    "attribute_type": "select",
    "type_display": "Select",
    "group": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "group_name": "Technical Specifications",
    "is_required": true,
    "is_filterable": true,
    "is_searchable": true,
    "display_order": 1,
    "option_count": 5
  }
]
```

> **Note:** `option_count` is only populated for `select` and `multiselect` types. For other types it returns `null`.

### Create Attribute

```
POST /api/attributes/
```

**Request Body:**

```json
{
  "name": "Weight",
  "group": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "attribute_type": "number",
  "unit": "kg",
  "is_required": false,
  "is_filterable": true,
  "is_searchable": false,
  "is_comparable": true,
  "is_visible_on_product": true,
  "display_order": 2,
  "min_value": "0.0000",
  "max_value": "1000.0000",
  "categories": []
}
```

**Response** `201 Created`:

```json
{
  "id": "d4e5f6a7-b8c9-0123-defa-234567890123",
  "name": "Weight",
  "slug": "weight",
  "group": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "group_name": "Technical Specifications",
  "attribute_type": "number",
  "type_display": "Number",
  "unit": "kg",
  "is_required": false,
  "is_filterable": true,
  "is_searchable": false,
  "is_comparable": true,
  "is_visible_on_product": true,
  "display_order": 2,
  "validation_regex": "",
  "min_value": "0.0000",
  "max_value": "1000.0000",
  "categories": [],
  "is_active": true,
  "created_on": "2026-01-15T11:30:00Z",
  "updated_on": "2026-01-15T11:30:00Z"
}
```

### Retrieve Attribute (Detail)

```
GET /api/attributes/{id}/
```

Returns a detailed representation with nested group and options.

**Response** `200 OK`:

```json
{
  "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "name": "Color",
  "slug": "color",
  "group": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Technical Specifications",
    "slug": "technical-specifications",
    "description": "",
    "display_order": 1,
    "is_active": true,
    "attribute_count": 5,
    "created_on": "2026-01-15T10:30:00Z",
    "updated_on": "2026-01-15T10:30:00Z"
  },
  "attribute_type": "select",
  "type_display": "Select",
  "unit": "",
  "is_required": true,
  "is_filterable": true,
  "is_searchable": true,
  "is_comparable": false,
  "is_visible_on_product": true,
  "display_order": 1,
  "validation_regex": "",
  "min_value": null,
  "max_value": null,
  "categories": [],
  "options": [
    {
      "id": "e5f6a7b8-c9d0-1234-efab-345678901234",
      "attribute": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "attribute_name": "Color",
      "value": "red",
      "label": "Bright Red",
      "color_code": "#FF0000",
      "image": null,
      "display_order": 1,
      "is_default": false,
      "created_on": "2026-01-15T12:00:00Z",
      "updated_on": "2026-01-15T12:00:00Z"
    }
  ],
  "option_count": 1,
  "is_active": true,
  "created_on": "2026-01-15T11:00:00Z",
  "updated_on": "2026-01-15T11:00:00Z"
}
```

### Update Attribute

```
PUT /api/attributes/{id}/
PATCH /api/attributes/{id}/
```

Uses the standard serializer (not detail). Include `group` as UUID.

### Delete Attribute

```
DELETE /api/attributes/{id}/
```

**Response** `204 No Content`

> Deleting an attribute will CASCADE delete all its options.

### Attributes by Category

```
GET /api/attributes/by-category/?category_id={uuid}
```

Returns all attributes assigned to the given category **and its parent categories** (inheritance). This is used to build product forms with all relevant attributes.

**Query Parameters:**

| Parameter     | Type | Required | Description                      |
| ------------- | ---- | -------- | -------------------------------- |
| `category_id` | UUID | Yes      | Category to fetch attributes for |

**Response** `200 OK`: Array of detailed attribute objects (same shape as retrieve).

**Error** `400 Bad Request`:

```json
{
  "error": "category_id query parameter is required."
}
```

**Error** `404 Not Found`: If category does not exist.

### Filterable Attributes

```
GET /api/attributes/filterable/?category_id={uuid}
```

Returns attributes marked as `is_filterable=True`, optionally filtered by category. Used to build faceted search filters in the webstore.

**Query Parameters:**

| Parameter     | Type | Required | Description              |
| ------------- | ---- | -------- | ------------------------ |
| `category_id` | UUID | No       | Optional category filter |

**Response** `200 OK`: Array of detailed attribute objects.

---

## Attribute Options

### List Attribute Options

```
GET /api/attribute-options/
```

**Query Parameters:**

| Parameter    | Type    | Description                       |
| ------------ | ------- | --------------------------------- |
| `attribute`  | UUID    | Filter by attribute ID            |
| `is_default` | boolean | Filter by default status          |
| `ordering`   | string  | Order by `display_order`, `label` |

**Response** `200 OK`:

```json
[
  {
    "id": "e5f6a7b8-c9d0-1234-efab-345678901234",
    "attribute": "c3d4e5f6-a7b8-9012-cdef-123456789012",
    "attribute_name": "Color",
    "value": "red",
    "label": "Bright Red",
    "color_code": "#FF0000",
    "image": null,
    "display_order": 1,
    "is_default": false,
    "created_on": "2026-01-15T12:00:00Z",
    "updated_on": "2026-01-15T12:00:00Z"
  }
]
```

### Create Attribute Option

```
POST /api/attribute-options/
```

**Request Body:**

```json
{
  "attribute": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "value": "green",
  "label": "Forest Green",
  "color_code": "#228B22",
  "display_order": 3,
  "is_default": false
}
```

**Response** `201 Created`: Created option object.

### Retrieve Attribute Option

```
GET /api/attribute-options/{id}/
```

**Response** `200 OK`: Option object.

### Update Attribute Option

```
PUT /api/attribute-options/{id}/
PATCH /api/attribute-options/{id}/
```

### Delete Attribute Option

```
DELETE /api/attribute-options/{id}/
```

**Response** `204 No Content`

---

## Error Codes

| Status Code              | Description                                                                                        |
| ------------------------ | -------------------------------------------------------------------------------------------------- |
| `400 Bad Request`        | Validation error (e.g., min_value > max_value, missing required fields, duplicate attribute+value) |
| `401 Unauthorized`       | Missing or invalid authentication token                                                            |
| `403 Forbidden`          | Insufficient permissions                                                                           |
| `404 Not Found`          | Resource does not exist                                                                            |
| `405 Method Not Allowed` | HTTP method not supported on endpoint                                                              |
