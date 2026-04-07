# API Versioning

> Versioning strategy, lifecycle, and deprecation policy.

**Navigation:** [API Overview](overview.md) · [Errors](errors.md) · [Docs Index](../index.md)

---

## Overview

LankaCommerce Cloud API uses **URL-based versioning** to manage breaking changes while maintaining backward compatibility for existing clients.

---

## Versioning Strategy

| Aspect              | Details                                        |
| ------------------- | ---------------------------------------------- |
| **Method**          | URL path prefix — `/api/v1/`, `/api/v2/`, etc. |
| **Current Version** | `v1`                                           |
| **Format**          | `v` followed by a major version number         |

All endpoints are prefixed with the version:

| Version     | Base Path  |
| ----------- | ---------- |
| v1          | `/api/v1/` |
| v2 (future) | `/api/v2/` |

---

## What Constitutes a Breaking Change

A new API version is required when any of the following changes are introduced:

| Change Type                             | Breaking? | Requires New Version? |
| --------------------------------------- | --------- | --------------------- |
| Removing an endpoint                    | Yes       | Yes                   |
| Removing a response field               | Yes       | Yes                   |
| Changing a field's data type            | Yes       | Yes                   |
| Making an optional field required       | Yes       | Yes                   |
| Changing authentication requirements    | Yes       | Yes                   |
| Adding a new optional field to response | No        | No                    |
| Adding a new optional query parameter   | No        | No                    |
| Adding a new endpoint                   | No        | No                    |
| Fixing a bug in response data           | No        | No                    |
| Performance improvements                | No        | No                    |

---

## Version Lifecycle

Each API version follows a defined lifecycle:

| Stage          | Duration                 | Description                                                   |
| -------------- | ------------------------ | ------------------------------------------------------------- |
| **Active**     | Ongoing                  | Fully supported, receives new features and bug fixes          |
| **Deprecated** | 6 months minimum         | Still functional but no new features — clients should migrate |
| **Sunset**     | After deprecation period | Removed — returns 410 Gone                                    |

---

## Deprecation Policy

When a version is deprecated:

1. **Announcement** — Deprecation is announced in the changelog and API documentation at least **6 months** before sunset
2. **Headers** — Deprecated endpoints include a `Sunset` header with the retirement date and a `Deprecation` header
3. **Documentation** — Migration guides are published showing how to update to the new version
4. **Monitoring** — Usage of deprecated endpoints is tracked to identify clients that need to migrate

### Deprecation Headers

| Header        | Description                                     |
| ------------- | ----------------------------------------------- |
| `Deprecation` | ISO 8601 date when the endpoint was deprecated  |
| `Sunset`      | ISO 8601 date when the endpoint will be removed |
| `Link`        | URL to the migration guide                      |

---

## Migration Between Versions

When migrating from one API version to another:

| Step | Action                                              |
| ---- | --------------------------------------------------- |
| 1    | Review the changelog for breaking changes           |
| 2    | Read the migration guide for the new version        |
| 3    | Update endpoint URLs in your client code            |
| 4    | Adjust request/response handling for changed fields |
| 5    | Test thoroughly in a development environment        |
| 6    | Deploy the updated client                           |

---

## Schema Versioning

The OpenAPI schema reflects the current API version:

| Endpoint       | Description                        |
| -------------- | ---------------------------------- |
| `/api/schema/` | Schema for all active versions     |
| `/api/docs/`   | Swagger UI for all active versions |
| `/api/redoc/`  | ReDoc for all active versions      |

The `SCHEMA_PATH_PREFIX` in drf-spectacular is configured as `/api/v[0-9]` to correctly scope endpoints by version.

---

## Best Practices

| Practice                    | Recommendation                                            |
| --------------------------- | --------------------------------------------------------- |
| Pin to a version            | Always include the version prefix in API requests         |
| Monitor deprecation headers | Watch for `Deprecation` and `Sunset` headers in responses |
| Subscribe to changelog      | Stay informed about upcoming breaking changes             |
| Test migrations early       | Begin migration as soon as a new version is released      |
| Avoid version-less URLs     | Never call `/api/` without a version prefix               |

---

## Related Documentation

- [API Overview](overview.md) — API architecture and entry points
- [Authentication](authentication.md) — JWT flows and token management
- [Errors Documentation](errors.md) — Error response formats
- [Docs Index](../index.md) — Documentation hub
