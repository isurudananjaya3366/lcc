# Inventory Module Documentation

Comprehensive documentation for the Inventory Management module of the LCC-POS system.

## Contents

| Document                        | Description                                                        |
| ------------------------------- | ------------------------------------------------------------------ |
| [Models](models.md)             | Data models — StockLevel, StockMovement, StockTake, StockTakeItem  |
| [Services](services.md)         | Business logic — StockService, AdjustmentService, StockTakeService |
| [API](api.md)                   | REST API endpoints, payloads, and response shapes                  |
| [Architecture](architecture.md) | Design decisions, concurrency strategy, and module structure       |

## Quick Start

The inventory module lives under `apps/inventory/stock/` and provides:

- **Real-time stock tracking** per product/variant/warehouse/location
- **Movement audit trail** for every quantity change
- **Stock operations** — receive, dispatch, transfer, adjust
- **Stock takes** — full lifecycle from draft → counting → review → approval → completion
- **Concurrency safety** — row-level locking via `SELECT … FOR UPDATE`

## Module Location

```
apps/inventory/
├── stock/
│   ├── models/           # StockLevel, StockMovement, StockTake, StockTakeItem
│   ├── services/         # StockService, AdjustmentService, StockTakeService
│   ├── api/              # ViewSets, Serializers, URL routing
│   ├── constants.py      # Enums and threshold values
│   ├── exceptions.py     # StockOperationError
│   └── results.py        # OperationResult dataclass
└── warehouses/           # Warehouse, WarehouseZone, StorageLocation
```
