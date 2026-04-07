# API Pagination

> Pagination model, parameters, defaults, and usage guidance.

**Navigation:** [API Overview](overview.md) · [Errors](errors.md) · [Docs Index](../index.md)

---

## Overview

LankaCommerce Cloud API uses **page-number pagination** for all list endpoints. This approach provides predictable, offset-based navigation through large result sets.

---

## Pagination Model

All paginated responses share the same envelope structure:

| Field      | Type          | Description                                                         |
| ---------- | ------------- | ------------------------------------------------------------------- |
| `count`    | integer       | Total number of results across all pages                            |
| `next`     | string / null | Full URL for the next page, or `null` if this is the last page      |
| `previous` | string / null | Full URL for the previous page, or `null` if this is the first page |
| `results`  | array         | Array of resource objects for the current page                      |

---

## Query Parameters

| Parameter   | Type    | Default | Description                 |
| ----------- | ------- | ------- | --------------------------- |
| `page`      | integer | `1`     | The page number to retrieve |
| `page_size` | integer | `20`    | Number of results per page  |

---

## Defaults and Limits

| Setting           | Value | Source                                               |
| ----------------- | ----- | ---------------------------------------------------- |
| Default page size | 20    | `REST_FRAMEWORK["PAGE_SIZE"]` in settings            |
| Maximum page size | 100   | Enforced by the API — requests above this are capped |
| First page        | 1     | Pages are 1-indexed                                  |

---

## Usage

### Requesting a Specific Page

| Request                                     | Description                        |
| ------------------------------------------- | ---------------------------------- |
| `GET /api/v1/products/`                     | First page, default page size (20) |
| `GET /api/v1/products/?page=3`              | Third page, default page size      |
| `GET /api/v1/products/?page=2&page_size=50` | Second page, 50 results per page   |

### Navigating Pages

Use the `next` and `previous` URLs from the response to navigate between pages. These are full URLs that include all necessary query parameters.

| Response Field           | Action                                   |
| ------------------------ | ---------------------------------------- |
| `next` is not `null`     | More pages available — follow the URL    |
| `next` is `null`         | This is the last page                    |
| `previous` is not `null` | Earlier pages available — follow the URL |
| `previous` is `null`     | This is the first page                   |

---

## Combining with Filters

Pagination works seamlessly with filtering, searching, and ordering:

| Request                                             | Description                  |
| --------------------------------------------------- | ---------------------------- |
| `GET /api/v1/products/?category=electronics&page=2` | Filtered and paginated       |
| `GET /api/v1/products/?search=laptop&page_size=10`  | Search with custom page size |
| `GET /api/v1/products/?ordering=-created_at&page=1` | Ordered and paginated        |

The `count` field reflects the total number of results **after filters are applied**.

---

## Edge Cases

| Scenario                    | Behavior                                                          |
| --------------------------- | ----------------------------------------------------------------- |
| Page out of range           | Returns 404 with `"Invalid page."`                                |
| `page_size` exceeds maximum | Capped to maximum (100)                                           |
| `page_size=0` or negative   | Returns 400 Bad Request                                           |
| Empty result set            | Returns `count: 0`, `results: []`, `next: null`, `previous: null` |

---

## Best Practices

| Practice                      | Recommendation                                                                 |
| ----------------------------- | ------------------------------------------------------------------------------ |
| Use `next`/`previous` URLs    | Always navigate using the provided URLs rather than constructing them manually |
| Request reasonable page sizes | Keep page sizes between 10 and 50 for optimal performance                      |
| Display total count           | Show `count` to users so they know the full result set size                    |
| Handle empty results          | Gracefully handle `results: []` in the UI                                      |
| Cache awareness               | Paginated responses may be cached — respect cache headers                      |

---

## Related Documentation

- [API Overview](overview.md) — API architecture and entry points
- [Errors Documentation](errors.md) — Error response formats
- [Rate Limiting](rate-limiting.md) — Throttle limits and headers
- [Docs Index](../index.md) — Documentation hub
