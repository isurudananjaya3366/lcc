# Order Module — Fulfillment Workflow

## Overview

The fulfillment workflow manages the physical process of getting ordered items from warehouse to customer. It supports partial fulfillment, multiple warehouses, and carrier tracking.

## Fulfillment Status Flow

```
PENDING → PROCESSING → PICKING → PICKED → PACKING → PACKED → SHIPPED → DELIVERED
                                                                          ↓
Any pre-ship state → CANCELLED                                         FAILED
```

## Workflow Steps

### 1. Order Confirmation (Task 57)

When an order is confirmed (`FulfillmentService.confirm_order()`):

- Validates order is in PENDING status
- Transitions to CONFIRMED
- Sends confirmation notification to customer

### 2. Start Processing (Task 58)

When processing begins (`FulfillmentService.start_processing()`):

- Transitions order to PROCESSING
- Creates initial Fulfillment record
- Creates FulfillmentLineItem entries for all order items
- Notifies warehouse team to begin picking

### 3. Pick Items (Task 59)

Warehouse staff picks items (`FulfillmentService.pick_items()`):

- Validates fulfillment is in PENDING/PROCESSING/PICKING state
- Records `picked_at`, `picked_by`, and `bin_location` per item
- When all items picked, fulfillment transitions to PICKED

### 4. Pack Order (Task 60)

Items are packed for shipping (`FulfillmentService.pack_order()`):

- Validates fulfillment is in PICKED/PACKING state
- Records package details: weight, dimensions, special handling
- Calculates volumetric weight
- Marks all items as packed
- Sets fulfillment packed_at timestamp
- Transitions to PACKED

### 5. Ship Order (Task 61)

Fulfillment is handed to carrier (`FulfillmentService.ship_order()`):

- Validates fulfillment is in PACKED state
- Records carrier, tracking number, carrier service
- Auto-generates tracking URL
- Updates order line item `quantity_fulfilled`
- Transitions order to SHIPPED (if all items shipped)
- Logs shipment event in order history
- Sends shipping notification to customer

### 6. Delivery Confirmation (Task 63)

Carrier confirms delivery (`FulfillmentService.confirm_delivery()`):

- Validates fulfillment is in SHIPPED state
- Records recipient, signature, photo, delivery timestamp
- Updates order line items `delivered_at`
- If all fulfillments delivered, transitions order to DELIVERED
- Logs delivery event
- Sends delivery notification

### 7. Order Completion (Task 64)

Final step (`FulfillmentService.complete_order()`):

- Validates order is in DELIVERED state
- Transitions to COMPLETED
- Locks the order automatically
- Sends completion notification

## Partial Fulfillment (Task 62)

When not all items can be shipped together:

1. `FulfillmentService.create_partial_fulfillment()` creates a new fulfillment with selected items
2. Order status moves to `PARTIALLY_FULFILLED`
3. Each partial fulfillment goes through the full pick → pack → ship → deliver workflow independently
4. When the last fulfillment ships, order transitions to SHIPPED
5. Customer receives notification for each partial shipment

## Tracking

Carrier tracking URLs are auto-generated for supported carriers:

- DHL, FedEx, UPS, Aramex, Sri Lanka Post

The `check_delivery_status_async` Celery task periodically polls tracking status for shipped fulfillments.

## Package Management

Each fulfillment tracks:

- **Weight** (actual and volumetric) — chargeable weight is the greater value
- **Dimensions** (L × W × H in cm)
- **Package type** (box, envelope, pallet)
- **Special handling** flags (fragile, requires signature)
- **International shipping** with customs value and description
