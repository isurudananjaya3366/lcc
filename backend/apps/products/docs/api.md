# Category API — Endpoint Reference

Base URL: `/api/v1/categories/`

All endpoints require **authentication** (`IsAuthenticated`).

---

## Endpoints

| Method   | URL                             | Action         | Description                         |
| -------- | ------------------------------- | -------------- | ----------------------------------- |
| `GET`    | `/api/v1/categories/`           | list           | List categories (paginated)         |
| `POST`   | `/api/v1/categories/`           | create         | Create a category                   |
| `GET`    | `/api/v1/categories/{id}/`      | retrieve       | Get category detail                 |
| `PUT`    | `/api/v1/categories/{id}/`      | update         | Full update                         |
| `PATCH`  | `/api/v1/categories/{id}/`      | partial_update | Partial update                      |
| `DELETE` | `/api/v1/categories/{id}/`      | destroy        | Delete category (cascades children) |
| `GET`    | `/api/v1/categories/tree/`      | tree           | Full recursive tree                 |
| `POST`   | `/api/v1/categories/{id}/move/` | move           | Move node in tree                   |

---

## List Categories

```
GET /api/v1/categories/
```

### Query parameters

| Parameter   | Type          | Description                                                                                                        |
| ----------- | ------------- | ------------------------------------------------------------------------------------------------------------------ |
| `parent`    | UUID or empty | Filter by parent ID. `?parent=` (empty) returns root categories only.                                              |
| `is_active` | bool          | `true` / `false` — filter by active status.                                                                        |
| `search`    | string        | Full-text search across `name` and `description`.                                                                  |
| `ordering`  | string        | Order by `name`, `display_order`, or `created_on`. Prefix with `-` for descending. Default: `display_order, name`. |

### Response `200 OK`

```json
[
  {
    "id": "a1b2c3d4-...",
    "name": "Electronics",
    "slug": "electronics",
    "icon": "fas fa-tv",
    "parent": null,
    "is_active": true,
    "display_order": 0,
    "level": 0
  },
  {
    "id": "e5f6a7b8-...",
    "name": "Clothing",
    "slug": "clothing",
    "icon": "fas fa-tshirt",
    "parent": null,
    "is_active": true,
    "display_order": 1,
    "level": 0
  }
]
```

---

## Create Category

```
POST /api/v1/categories/
Content-Type: application/json
```

### Request body

| Field             | Type         | Required | Description                                     |
| ----------------- | ------------ | -------- | ----------------------------------------------- |
| `name`            | string       | **yes**  | Category name (max 255 chars).                  |
| `slug`            | string       | no       | Auto-generated from `name` if omitted or blank. |
| `parent`          | UUID \| null | no       | Parent category ID. `null` or omitted → root.   |
| `description`     | string       | no       | Category description.                           |
| `image`           | file         | no       | Category image (multipart upload).              |
| `icon`            | string       | no       | CSS icon class.                                 |
| `is_active`       | boolean      | no       | Default `true`.                                 |
| `display_order`   | integer      | no       | Default `0`.                                    |
| `seo_title`       | string       | no       | Meta title.                                     |
| `seo_description` | string       | no       | Meta description.                               |
| `seo_keywords`    | string       | no       | Comma-separated keywords.                       |

### Example request

```json
{
  "name": "Mobile Phones",
  "parent": "a1b2c3d4-...",
  "icon": "fas fa-mobile-alt",
  "description": "Smartphones and feature phones",
  "is_active": true,
  "display_order": 0
}
```

### Response `201 Created`

```json
{
  "name": "Mobile Phones",
  "slug": "mobile-phones",
  "parent": "a1b2c3d4-...",
  "description": "Smartphones and feature phones",
  "image": null,
  "icon": "fas fa-mobile-alt",
  "is_active": true,
  "display_order": 0,
  "seo_title": "",
  "seo_description": "",
  "seo_keywords": ""
}
```

### Validation errors `400 Bad Request`

```json
{
  "name": ["Category name cannot be blank."],
  "parent": ["A category cannot be its own parent."]
}
```

---

## Retrieve Category

```
GET /api/v1/categories/{id}/
```

### Response `200 OK`

```json
{
  "id": "e5f6a7b8-...",
  "name": "Mobile Phones",
  "slug": "mobile-phones",
  "parent": "a1b2c3d4-...",
  "parent_name": "Electronics",
  "description": "Smartphones and feature phones",
  "image": null,
  "icon": "fas fa-mobile-alt",
  "is_active": true,
  "display_order": 0,
  "children_count": 2,
  "created_on": "2026-03-10T08:00:00Z",
  "updated_on": "2026-03-10T08:00:00Z",
  "seo_title": "",
  "seo_description": "",
  "seo_keywords": "",
  "is_root": false,
  "is_leaf": false,
  "descendants_count": 2,
  "full_path": "Electronics > Mobile Phones",
  "children": [
    {
      "id": "...",
      "name": "Smartphones",
      "slug": "smartphones",
      "icon": "fas fa-mobile-alt",
      "parent": "e5f6a7b8-...",
      "is_active": true,
      "display_order": 0,
      "level": 2
    },
    {
      "id": "...",
      "name": "Feature Phones",
      "slug": "feature-phones",
      "icon": "fas fa-phone",
      "parent": "e5f6a7b8-...",
      "is_active": true,
      "display_order": 1,
      "level": 2
    }
  ]
}
```

### Not found `404 Not Found`

```json
{
  "detail": "Not found."
}
```

---

## Update Category

```
PUT /api/v1/categories/{id}/
```

Send **all** writable fields. On `PUT`, if `slug` is blank and `name` changed, a new unique slug is auto-generated.

### Response `200 OK`

Returns the updated category (same shape as create response).

---

## Partial Update

```
PATCH /api/v1/categories/{id}/
```

Send only the fields to update.

```json
{
  "is_active": false
}
```

### Response `200 OK`

Returns the updated category.

---

## Delete Category

```
DELETE /api/v1/categories/{id}/
```

> **Warning:** Deleting a parent category will **cascade-delete** all its descendants due to `on_delete=CASCADE`.

### Response `204 No Content`

_(empty body)_

---

## Tree

```
GET /api/v1/categories/tree/
```

Returns the full category tree as a recursive nested structure.

### Query parameters

| Parameter     | Type | Default | Description                                                  |
| ------------- | ---- | ------- | ------------------------------------------------------------ |
| `active_only` | bool | `true`  | `true` — only active categories. `false` — include inactive. |

### Response `200 OK`

```json
[
  {
    "id": "a1b2c3d4-...",
    "name": "Electronics",
    "slug": "electronics",
    "icon": "fas fa-tv",
    "is_active": true,
    "display_order": 0,
    "level": 0,
    "children": [
      {
        "id": "e5f6a7b8-...",
        "name": "Mobile Phones",
        "slug": "mobile-phones",
        "icon": "fas fa-mobile-alt",
        "is_active": true,
        "display_order": 0,
        "level": 1,
        "children": [
          {
            "id": "...",
            "name": "Smartphones",
            "slug": "smartphones",
            "icon": "fas fa-mobile-alt",
            "is_active": true,
            "display_order": 0,
            "level": 2,
            "children": []
          }
        ]
      }
    ]
  }
]
```

---

## Move Category

```
POST /api/v1/categories/{id}/move/
Content-Type: application/json
```

Move a category to a new position in the tree.

### Request body

| Field      | Type         | Required | Description                                                           |
| ---------- | ------------ | -------- | --------------------------------------------------------------------- |
| `target`   | UUID \| null | **yes**  | Target parent ID. `null` → make root.                                 |
| `position` | string       | no       | `first-child` (default: `last-child`), `last-child`, `left`, `right`. |

### Example: move under a new parent

```json
{
  "target": "a1b2c3d4-...",
  "position": "first-child"
}
```

### Example: make root

```json
{
  "target": null,
  "position": "last-child"
}
```

### Response `200 OK`

Returns the full detail representation of the moved category (same shape as retrieve).

### Error responses

**Invalid position** `400 Bad Request`

```json
{
  "detail": "Invalid position."
}
```

**Target not found** `404 Not Found`

```json
{
  "detail": "Target category not found."
}
```

**Cycle detected** `400 Bad Request`

```json
{
  "detail": "Cannot move a category to its own descendant."
}
```

---

## Authentication

All endpoints require an authenticated request. Include a valid token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Unauthenticated requests receive:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Status:** `401 Unauthorized`

---

## Common Error Responses

| Status | Meaning            | When                                               |
| ------ | ------------------ | -------------------------------------------------- |
| `400`  | Bad Request        | Validation error, invalid position, cycle detected |
| `401`  | Unauthorized       | Missing or invalid token                           |
| `404`  | Not Found          | Category ID does not exist                         |
| `405`  | Method Not Allowed | Wrong HTTP method for endpoint                     |
