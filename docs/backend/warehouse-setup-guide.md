# Warehouse Module — Setup Guide

Quick-start guide for developing against the warehouse & locations module.

---

## Prerequisites

- Docker & Docker Compose running
- Database migrations applied
- At least one tenant schema provisioned

## 1. Apply Migrations

```bash
docker compose exec backend python manage.py migrate_schemas --shared
docker compose exec backend python manage.py migrate_schemas --tenant
```

The warehouse module uses five migrations:

| Migration                           | Content                                                                                      |
| ----------------------------------- | -------------------------------------------------------------------------------------------- |
| `0002_warehouse`                    | Warehouse model                                                                              |
| `0003_storage_location`             | StorageLocation (hierarchy)                                                                  |
| `0004_barcode_scan`                 | BarcodeScan audit model                                                                      |
| `0005_group_d_warehouse_operations` | WarehouseZone, TransferRoute, WarehouseCapacity, DefaultWarehouseConfig, POSWarehouseMapping |

## 2. Verify Models Load

```bash
docker compose exec backend python -c "
from apps.inventory.warehouses.models import (
    Warehouse, StorageLocation, BarcodeScan,
    WarehouseZone, TransferRoute, WarehouseCapacity,
    DefaultWarehouseConfig, POSWarehouseMapping,
)
print('All 8 models imported successfully')
"
```

## 3. Verify Admin Registration

```bash
docker compose exec backend python -c "
from django.contrib.admin.sites import site
registered = [m.__name__ for m in site._registry]
warehouse_models = [
    'Warehouse', 'StorageLocation', 'BarcodeScan',
    'WarehouseZone', 'TransferRoute', 'WarehouseCapacity',
    'DefaultWarehouseConfig', 'POSWarehouseMapping',
]
for m in warehouse_models:
    status = 'OK' if m in registered else 'MISSING'
    print(f'  {m}: {status}')
"
```

## 4. Verify API URLs

```bash
docker compose exec backend python -c "
from apps.inventory.warehouses.api.urls import router
for prefix, viewset, basename in router.registry:
    print(f'  /{prefix}/ → {viewset.__name__}')
"
```

Expected output:

```
  warehouses/ → WarehouseViewSet
  locations/ → StorageLocationViewSet
  zones/ → WarehouseZoneViewSet
  routes/ → TransferRouteViewSet
  capacities/ → WarehouseCapacityViewSet
```

## 5. Run Tests

```bash
# Unit tests (no database required)
docker compose exec backend python -m pytest tests/inventory/ -v

# With coverage
docker compose exec backend python -m pytest tests/inventory/ -v --cov=apps.inventory.warehouses
```

## 6. Key Configuration

### Constants (`apps/inventory/warehouses/constants.py`)

| Constant                        | Default | Description              |
| ------------------------------- | ------- | ------------------------ |
| `BARCODE_PREFIX_LOCATION`       | `"LOC"` | Barcode prefix           |
| `BARCODE_SEPARATOR`             | `"-"`   | Part separator           |
| `BARCODE_TENANT_PREFIX_LENGTH`  | `3`     | Tenant code chars        |
| `BARCODE_WAREHOUSE_CODE_LENGTH` | `6`     | Max warehouse code chars |
| `BARCODE_LOCATION_CODE_LENGTH`  | `15`    | Max location code chars  |

### Location Hierarchy

```
zone (depth 0)
  └── aisle (depth 1)
       └── rack (depth 2)
            └── shelf (depth 3)
                 └── bin (depth 4)
```

Parent rules are enforced in `LOCATION_PARENT_RULES` — e.g., an aisle's
parent must be a zone.

## 7. Common Development Tasks

### Create a warehouse (Django shell)

```python
from apps.inventory.warehouses.models import Warehouse
wh = Warehouse.objects.create(
    name="Colombo Main",
    code="WH-CMB-01",
    warehouse_type="main",
    city="Colombo",
    district="colombo",
)
```

### Generate a barcode

```python
from apps.inventory.warehouses.services.barcode_generator import BarcodeGenerator
gen = BarcodeGenerator()
barcode = gen.generate_location_barcode(location)
```

### Calculate transfer cost

```python
route = TransferRoute.objects.get(
    source_warehouse=wh_a,
    destination_warehouse=wh_b,
)
cost = route.calculate_transfer_cost(weight_kg=50, volume_m3=2.0)
```
