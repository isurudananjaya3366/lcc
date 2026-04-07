# Inventory Management User Guide

A practical guide for managing inventory in the LCC-POS system.

---

## Overview

The inventory system tracks every product across all your warehouses. You can:

- **Receive stock** when deliveries arrive
- **Dispatch stock** for sales and orders
- **Transfer stock** between warehouses
- **Adjust stock** for corrections (damage, found items, etc.)
- **Conduct stock takes** to verify physical counts against the system

---

## Daily Operations

### Receiving Stock (Stock-In)

When a shipment arrives:

1. Navigate to **Inventory → Stock Operations**
2. Select **Stock In**
3. Choose the product, warehouse, and quantity
4. Enter the cost per unit (for accurate valuation)
5. Add a reference (e.g., Purchase Order number) for traceability
6. Submit

The system will:

- Increase the stock level for that product/warehouse
- Record a movement in the audit trail
- Update the weighted-average cost

### Dispatching Stock (Stock-Out)

When fulfilling orders:

1. Navigate to **Inventory → Stock Operations**
2. Select **Stock Out**
3. Choose the product, warehouse, and quantity
4. Select a reason (sale, damage, etc.)
5. Submit

The system checks that sufficient stock is available before processing. If stock is insufficient, the operation is rejected.

### Transferring Stock

To move stock between warehouses:

1. Navigate to **Inventory → Stock Operations**
2. Select **Transfer**
3. Choose the product, source warehouse, destination warehouse, and quantity
4. Submit

The transfer is atomic — the source is debited and the destination is credited in a single operation. If anything fails, neither side is affected.

---

## Stock Monitoring

### Viewing Stock Levels

Navigate to **Inventory → Stock Levels** to see current stock positions.

Each row shows:

- **Quantity**: Physical stock on hand
- **Reserved**: Quantity held for pending orders
- **Available**: Quantity minus reserved (what you can sell)
- **Incoming**: Expected from purchase orders
- **Status**: Out of Stock / Critical / Low / Adequate / Overstock

### Low Stock Alerts

Products where the available quantity falls below the **reorder point** are flagged as low stock. Use the **Low Stock** filter to find items that need reordering.

### Out of Stock

Products with zero quantity are shown in the **Out of Stock** view.

---

## Stock Takes (Physical Inventory Counts)

### When to Conduct Stock Takes

- **Full count**: Annual or semi-annual complete inventory
- **Cycle count**: Regular partial counts (rotating through products)
- **Spot check**: When discrepancies are suspected

### Creating a Stock Take

1. Navigate to **Inventory → Stock Takes**
2. Click **New Stock Take**
3. Select the target warehouse
4. Give it a name (e.g., "Q1 2025 Cycle Count")
5. Choose the scope: Full, Partial, or Cycle
6. Optionally enable **Blind Count** (hides expected quantities from counters)
7. Submit

### Counting Process

1. **Start** the stock take — the system snapshots current stock levels
2. Count each item physically and enter the counted quantity
3. Use **Bulk Count** to enter multiple items at once for efficiency
4. The system automatically calculates variances

### Review & Approval

1. **Submit for Review** when counting is complete
2. A supervisor reviews variances:
   - **Minor** (≤2%): Likely counting errors
   - **Moderate** (≤5%): Investigate
   - **Significant** (≤10%): Requires explanation
   - **Critical** (>10%): Must be explained before approval
3. **Approve** or **Reject** (sends back to counting with feedback)

### Completing a Stock Take

Once approved, **Complete** the stock take. The system will:

- Lock all item counts
- Create adjustment movements for each variance
- Update stock levels to match physical counts
- Record the full audit trail

### Cancelling

Stock takes can be cancelled at any point before completion. Cancelled stock takes are preserved for audit but have no effect on stock levels.

---

## Stock Adjustments

For manual corrections outside of stock takes:

1. Navigate to **Inventory → Stock Operations → Adjust**
2. Choose direction: **Up** (found extra stock) or **Down** (damaged, expired, etc.)
3. Enter the product, warehouse, quantity, and reason
4. Submit

Adjustments above the authorisation threshold (100 units by default) may require supervisor approval.

---

## Understanding the Audit Trail

Every stock change creates an immutable **Stock Movement** record. Navigate to **Inventory → Stock Movements** to view the full history.

Each movement shows:

- **Type**: In, Out, Transfer, Adjustment, Return, Reservation, Release
- **Reason**: Purchase, Sale, Damage, Found, etc.
- **Reference**: Link to the source document (PO, SO, etc.)
- **Who** performed the operation and **when**

Movements can be filtered by product, warehouse, date range, and type.

---

## Tips & Best Practices

1. **Always enter cost per unit** during stock-in to maintain accurate valuation.
2. **Use references** (PO numbers, SO numbers) to link movements to business documents.
3. **Conduct cycle counts regularly** rather than relying on annual full counts.
4. **Enable blind counts** for more objective stock takes.
5. **Investigate significant variances** promptly — they may indicate theft, damage, or systematic errors.
6. **Review low-stock alerts daily** to prevent stockouts.
7. **Use transfers** instead of manual adjustments when moving stock between locations.
