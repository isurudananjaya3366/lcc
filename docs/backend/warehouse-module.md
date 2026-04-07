# Warehouse & Locations Module

> **App path:** `apps.inventory.warehouses`
> **API namespace:** `warehouse`
> **Base URL:** `/api/v1/warehouse/`

## Overview

The Warehouse & Locations module manages physical warehouses, hierarchical
storage locations, barcode-based operations, transfer routes, and capacity
tracking within the multi-tenant inventory system.

---

## Models

| Model                    | DB Table                              | Description                                                        |
| ------------------------ | ------------------------------------- | ------------------------------------------------------------------ |
| `Warehouse`              | `inventory_warehouses`                | Physical warehouse with address, operating hours, and default flag |
| `StorageLocation`        | `inventory_storage_locations`         | Hierarchical location tree (zone → aisle → rack → shelf → bin)     |
| `WarehouseZone`          | `inventory_warehouse_zones`           | Logical grouping within a warehouse (picking, receiving, etc.)     |
| `BarcodeScan`            | `inventory_barcode_scans`             | Audit log of barcode scan events                                   |
| `TransferRoute`          | `inventory_transfer_routes`           | Inter-warehouse transfer route with cost calculation               |
| `WarehouseCapacity`      | `inventory_warehouse_capacities`      | Real-time capacity tracking (items, weight, volume)                |
| `DefaultWarehouseConfig` | `inventory_default_warehouse_configs` | User/system default warehouse preferences                          |
| `POSWarehouseMapping`    | `inventory_pos_warehouse_mappings`    | POS terminal ↔ warehouse binding                                   |

### Warehouse

Inherits `BaseModel` (`UUIDMixin + AuditMixin + StatusMixin + SoftDeleteMixin`).

Key fields: `name`, `code` (unique, max 50), `warehouse_type`, `status`,
Sri Lankan address fields (`address_line_1/2`, `city`, `district`, `postal_code`),
`phone`, `email`, `manager_name`, `is_default`, operating hours
(`is_24_hours`, `opens_at`, `closes_at`, `breaks_start`, `breaks_end`),
GPS coordinates (`latitude`, `longitude`).

Key methods:

- `is_open_at(dt)` — checks if open at a given datetime
- `set_as_default()` — atomically marks warehouse as default
- `clean()` — validates business rules

### StorageLocation

Self-referential tree with `parent` FK. Location types follow a strict
hierarchy enforced by `LOCATION_PARENT_RULES`:

```
zone → aisle → rack → shelf → bin
```

Key properties:

- `depth` — integer depth from `LOCATION_DEPTH_MAP`
- `level_name` — human-readable level name
- `location_path` — full path string (`" > "` separated)

Barcode field stores the generated barcode string (blank by default).

---

## Services

| Service            | Module                       | Purpose                                         |
| ------------------ | ---------------------------- | ----------------------------------------------- |
| `BarcodeGenerator` | `services.barcode_generator` | Generate, validate, and parse location barcodes |
| `BarcodeLookup`    | `services.barcode_lookup`    | Look up locations by scanned barcode            |
| `LabelGenerator`   | `services.label_generator`   | Generate printable barcode labels               |
| `ScanAnalytics`    | `services.scan_analytics`    | Aggregate scan statistics and trends            |
| `RouteFinder`      | `services.route_finder`      | Find optimal transfer routes between warehouses |
| `DashboardService` | `services.dashboard`         | Warehouse dashboard data aggregation            |

### Barcode Format

```
LOC-{TENANT_PREFIX}-{WAREHOUSE_CODE}-{LOCATION_CODE}-{CHECK_DIGIT}
```

- **TENANT_PREFIX**: 3-char uppercase derived from tenant code/name
- **WAREHOUSE_CODE**: up to 6 alphanumeric chars
- **LOCATION_CODE**: up to 15 alphanumeric chars
- **CHECK_DIGIT**: single Luhn digit for tamper detection

---

## API Endpoints

### Warehouses (`/api/v1/warehouse/warehouses/`)

| Method    | Path                 | Action                   |
| --------- | -------------------- | ------------------------ |
| GET       | `/`                  | List warehouses          |
| POST      | `/`                  | Create warehouse         |
| GET       | `/{id}/`             | Retrieve warehouse       |
| PUT/PATCH | `/{id}/`             | Update warehouse         |
| DELETE    | `/{id}/`             | Delete warehouse         |
| POST      | `/{id}/set_default/` | Set as default warehouse |
| GET       | `/{id}/dashboard/`   | Warehouse dashboard data |
| GET       | `/{id}/capacity/`    | Capacity summary         |

### Storage Locations (`/api/v1/warehouse/locations/`)

| Method    | Path                 | Action                      |
| --------- | -------------------- | --------------------------- |
| GET       | `/`                  | List locations (filterable) |
| POST      | `/`                  | Create location             |
| GET       | `/{id}/`             | Retrieve location           |
| PUT/PATCH | `/{id}/`             | Update location             |
| DELETE    | `/{id}/`             | Delete location             |
| GET       | `/{id}/children/`    | Direct child locations      |
| GET       | `/{id}/ancestors/`   | Ancestor chain to root      |
| GET       | `/{id}/descendants/` | All descendant locations    |
| GET       | `/{id}/siblings/`    | Sibling locations           |
| GET       | `/tree/`             | Full location tree          |
| GET       | `/barcode_lookup/`   | Look up by barcode          |
| POST      | `/bulk_create/`      | Bulk create locations       |

### Read-Only Endpoints

| Resource             | Base Path                       |
| -------------------- | ------------------------------- |
| Warehouse Zones      | `/api/v1/warehouse/zones/`      |
| Transfer Routes      | `/api/v1/warehouse/routes/`     |
| Warehouse Capacities | `/api/v1/warehouse/capacities/` |

---

## Serializers

| Serializer                        | Usage                            |
| --------------------------------- | -------------------------------- |
| `WarehouseListSerializer`         | Compact list view                |
| `WarehouseSerializer`             | Full detail with computed fields |
| `WarehouseCreateUpdateSerializer` | Create/update with validation    |
| `StorageLocationListSerializer`   | Compact list view                |
| `StorageLocationSerializer`       | Full detail with hierarchy info  |
| `LocationTreeSerializer`          | Recursive tree structure         |
| `WarehouseZoneSerializer`         | Zone CRUD                        |
| `TransferRouteSerializer`         | Route with cost details          |
| `WarehouseCapacitySerializer`     | Capacity metrics                 |
| `BulkLocationCreateSerializer`    | Bulk location creation payload   |

---

## Signals

- **`pre_save` on `StorageLocation`**: Auto-generates barcode via
  `BarcodeGenerator` when barcode field is empty.

---

## Admin

All 8 models are registered in Django admin with appropriate list displays,
filters, and search fields. Admin classes are defined in
`apps/inventory/warehouses/admin.py` and imported via `apps/inventory/admin.py`.

---

## Tests

Test files live in `tests/inventory/`:

| File                       | Scope                                                       | Tests |
| -------------------------- | ----------------------------------------------------------- | ----- |
| `test_warehouse_models.py` | All 8 models — meta, fields, `__str__`, properties, methods | 75+   |
| `test_barcode_services.py` | BarcodeGenerator, barcode signal                            | 15+   |
| `test_warehouse_api.py`    | Serializers, viewsets, URL routing                          | 50+   |

Run tests:

```bash
docker compose exec backend python -m pytest tests/inventory/ -v
```
