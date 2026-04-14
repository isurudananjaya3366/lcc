# Inventory Management Module

> Frontend documentation for the Inventory Management UI module.

## Overview

The Inventory Management module provides a comprehensive UI for managing stock levels, movements, adjustments, transfers, and warehouses. It is built with Next.js App Router, TanStack Table, TanStack Query, React Hook Form, and Zod validation.

## Route Structure

```
/inventory              → Stock Levels overview (default tab)
/inventory/movements    → Stock Movement history
/inventory/adjustments  → Stock Adjustments list
/inventory/adjustments/new → Create new adjustment
/inventory/transfers    → Stock Transfers list
/inventory/transfers/new → Create new transfer
/inventory/warehouses   → Warehouses list (card grid)
/inventory/warehouses/new → Create new warehouse
/inventory/warehouses/[id] → Edit warehouse
```

## Components

### Layout
- **`inventory/layout.tsx`** — Tab navigation with 5 tabs (Stock, Movements, Adjustments, Transfers, Warehouses)

### Stock Overview (`StockOverview/`)
| Component | Description |
|-----------|-------------|
| `StockOverview` | Main container with filters, sorting, pagination |
| `StockOverviewHeader` | Title + "New Adjustment" button |
| `StockSummaryCards` | Summary cards (Total, Low Stock, Out of Stock, Valuation) |
| `StockFilters` | Search, warehouse, stock level filters |
| `StockTable` | DataTable wrapper for stock levels |
| `StockTableColumns` | Column definitions for stock table |
| `StockLevelCell` | Status badge cell (In Stock/Low/Out/Overstocked) |
| `StockActionsCell` | Dropdown actions (View, Adjust, Transfer, History) |

### Movements (`Movements/`)
| Component | Description |
|-----------|-------------|
| `MovementsPage` | Main container with timeline/table toggle |
| `MovementsHeader` | Title with count badge + Export button |
| `MovementsFilters` | Date/type/product/warehouse filters |
| `ViewToggle` | Timeline/Table view switch |
| `MovementsTimeline` | Vertical timeline view |
| `MovementsTable` | DataTable view |
| `MovementTableColumns` | Column definitions |
| `MovementDetailModal` | Movement detail modal |

### Adjustments (`Adjustments/`)
| Component | Description |
|-----------|-------------|
| `AdjustmentsList` | List page with query |
| `AdjustmentsHeader` | Title + count + New button |
| `AdjustmentsTable` | DataTable wrapper |
| `AdjustmentTableColumns` | Column definitions |
| `AdjustmentForm` | Create form with RHF + Zod |
| `AdjustmentItems` | Dynamic item rows with useFieldArray |

### Transfers (`Transfers/`)
| Component | Description |
|-----------|-------------|
| `TransfersList` | List page with query |
| `TransfersHeader` | Title + status stats + New button |
| `TransfersTable` | DataTable wrapper |
| `TransferTableColumns` | Column definitions |
| `TransferStatusBadge` | Status badge (Pending/Completed/Cancelled) |
| `TransferForm` | Create form with warehouse selectors |
| `TransferItems` | Dynamic item rows |
| `ReceiveTransferDialog` | Receive/complete transfer dialog |

### Warehouses (`Warehouses/`)
| Component | Description |
|-----------|-------------|
| `WarehouseList` | List page with search |
| `WarehousesHeader` | Title + count + search + New button |
| `WarehouseCards` | Card grid layout |
| `WarehouseCard` | Individual card (name, address, stats, actions) |
| `WarehouseStats` | Capacity bar + active status |
| `WarehouseForm` | Create/Edit form |
| `WarehouseNameInput` | Name + code fields |
| `WarehouseAddressForm` | Address fields with Sri Lankan districts |
| `WarehouseSettings` | Default/Active toggle switches |
| `DeleteWarehouseDialog` | Delete confirmation with code verification |

## Hooks

### Query Hooks
| Hook | Source |
|------|--------|
| `useInventory` | `hooks/queries/useInventory.ts` |
| `useStockMovements` | `hooks/queries/useStockMovements.ts` |
| `useWarehouses` | `hooks/queries/useWarehouses.ts` |

### Mutation Hooks
| Hook | Source |
|------|--------|
| `useCreateStockAdjustment` | `hooks/mutations/useInventoryMutations.ts` |
| `useCreateStockTransfer` | `hooks/mutations/useInventoryMutations.ts` |
| `useApproveStockTransfer` | `hooks/mutations/useInventoryMutations.ts` |
| `useCompleteStockTransfer` | `hooks/mutations/useInventoryMutations.ts` |
| `useCancelStockTransfer` | `hooks/mutations/useInventoryMutations.ts` |
| `useCreateWarehouse` | `hooks/mutations/useInventoryMutations.ts` |
| `useUpdateWarehouse` | `hooks/mutations/useInventoryMutations.ts` |
| `useDeleteWarehouse` | `hooks/mutations/useInventoryMutations.ts` |

## API Integration

### Services
- **`inventoryService`** — Stock levels, movements, adjustments, transfers, counts, alerts, valuation
- **`warehouseService`** — Warehouse CRUD, locations

### Query Keys
All inventory queries use the `inventoryKeys` factory from `lib/queryKeys.ts`:
- `inventoryKeys.all()` — Base key for all inventory data
- `inventoryKeys.list(filters)` — Stock levels list
- `inventoryKeys.movements(filters)` — Movement queries
- `inventoryKeys.warehouses(filters)` — Warehouse queries

## Validation Schemas

| Schema | File | Fields |
|--------|------|--------|
| `adjustmentFormSchema` | `lib/validations/adjustment.ts` | warehouseId, reason, items[] |
| `transferFormSchema` | `lib/validations/transfer.ts` | source/dest warehouse, items[] |
| `warehouseFormSchema` | `lib/validations/warehouse.ts` | name, code, address, settings |

## Types

All inventory types are defined in `types/inventory.ts`:
- `StockLevel`, `StockMovement`, `StockAdjustment`, `StockTransfer`
- `Warehouse`, `WarehouseLocation`
- `StockMovementType`, `StockMovementStatus`, `AdjustmentReason`
- API request interfaces
