# Purchases Module

## Overview

The Purchases module manages the complete purchase order lifecycle from creation through goods receiving, including PDF generation, email notifications, and audit trail tracking.

## Models

| Model             | Description                                                       |
| ----------------- | ----------------------------------------------------------------- |
| **PurchaseOrder** | Core PO record with vendor, dates, financials, approval, shipping |
| **POLineItem**    | Individual line items on a PO with product, quantity, pricing     |
| **POHistory**     | Audit log tracking all changes to purchase orders                 |
| **POSettings**    | Per-tenant configuration (prefix, approval threshold, defaults)   |
| **GoodsReceipt**  | Record of goods received against a PO (GRN)                       |
| **GRNLineItem**   | Individual items received on a GRN with quantities and condition  |
| **POTemplate**    | PDF template configuration with company branding                  |

## Services

| Service                  | Purpose                                                                 |
| ------------------------ | ----------------------------------------------------------------------- |
| **POService**            | PO lifecycle: create, send, acknowledge, cancel, duplicate, consolidate |
| **POCalculationService** | Line total, subtotal, tax, and grand total calculations                 |
| **ReceivingService**     | Full/partial receiving, quality inspection, PO status updates           |
| **POPDFGenerator**       | PDF generation using reportlab with template support                    |
| **POEmailService**       | Email PO PDFs to vendors                                                |

## API Endpoints

### Purchase Orders

| Method | Endpoint                                    | Description            |
| ------ | ------------------------------------------- | ---------------------- |
| GET    | `/api/v1/purchase-orders/`                  | List POs with filters  |
| POST   | `/api/v1/purchase-orders/`                  | Create a new PO        |
| GET    | `/api/v1/purchase-orders/{id}/`             | Retrieve PO details    |
| PUT    | `/api/v1/purchase-orders/{id}/`             | Update PO (DRAFT only) |
| DELETE | `/api/v1/purchase-orders/{id}/`             | Delete PO              |
| POST   | `/api/v1/purchase-orders/{id}/send/`        | Send PO to vendor      |
| POST   | `/api/v1/purchase-orders/{id}/acknowledge/` | Record acknowledgement |
| POST   | `/api/v1/purchase-orders/{id}/cancel/`      | Cancel PO              |
| POST   | `/api/v1/purchase-orders/{id}/duplicate/`   | Duplicate PO as DRAFT  |
| POST   | `/api/v1/purchase-orders/{id}/receive/`     | Receive items          |

### Goods Receipts

| Method | Endpoint                       | Description          |
| ------ | ------------------------------ | -------------------- |
| GET    | `/api/v1/goods-receipts/`      | List GRNs            |
| GET    | `/api/v1/goods-receipts/{id}/` | Retrieve GRN details |

## PO Status Flow

```
DRAFT → SENT → ACKNOWLEDGED → PARTIAL_RECEIVED → RECEIVED → CLOSED
  ↓       ↓         ↓
CANCELLED CANCELLED CANCELLED
```

## Filters

- **Status**: `?status=draft`
- **Vendor**: `?vendor={uuid}`
- **Payment**: `?payment_status=unpaid`
- **Search**: `?search=PO-2025-00001`
- **Ordering**: `?ordering=-total`
