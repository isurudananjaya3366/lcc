# Vendor Module Documentation

## Overview

The Vendor Module provides comprehensive vendor/supplier management for the ERP system. It supports the full vendor lifecycle including onboarding, product catalog management, performance tracking, document management, and communication logging.

### Key Features

- **Vendor Management**: CRUD operations with status lifecycle (pending → active → inactive/blocked)
- **Contact Management**: Multiple contacts per vendor with roles and primary contact designation
- **Bank Accounts**: Vendor payment details with verification workflow
- **Address Management**: Multiple addresses per vendor (main, warehouse, billing, shipping)
- **Product Catalog**: Link products to vendors with vendor-specific pricing, MOQ, and lead times
- **Price Lists**: Tiered pricing with effective date ranges
- **Performance Tracking**: Delivery, quality, and response time metrics
- **Communication Logging**: Track all vendor interactions
- **Document Management**: Upload and track contracts, certificates, licenses
- **Import/Export**: CSV-based bulk import and export
- **History/Audit Trail**: Automatic tracking of vendor field changes

---

## Vendor Types

| Type             | Code           | Description                  |
| ---------------- | -------------- | ---------------------------- |
| Manufacturer     | `manufacturer` | Direct product manufacturers |
| Distributor      | `distributor`  | Product distributors         |
| Wholesaler       | `wholesaler`   | Bulk resellers               |
| Importer         | `importer`     | Product importers            |
| Service Provider | `service`      | Service-based vendors        |

## Vendor Status Lifecycle

```
pending_approval → active → inactive
                 → blocked
```

---

## API Reference

Base URL: `/api/v1/vendors/`

### Standard CRUD

| Method | Endpoint         | Description                          |
| ------ | ---------------- | ------------------------------------ |
| GET    | `/vendors/`      | List vendors (paginated, filterable) |
| POST   | `/vendors/`      | Create vendor                        |
| GET    | `/vendors/{id}/` | Get vendor detail                    |
| PUT    | `/vendors/{id}/` | Update vendor                        |
| PATCH  | `/vendors/{id}/` | Partial update                       |
| DELETE | `/vendors/{id}/` | Soft-delete vendor                   |

### Custom Actions

| Method   | Endpoint                        | Description              |
| -------- | ------------------------------- | ------------------------ |
| GET      | `/vendors/search/?q=term`       | Search vendors           |
| GET      | `/vendors/export/`              | Export vendors to CSV    |
| POST     | `/vendors/import/`              | Import vendors from CSV  |
| GET/POST | `/vendors/{id}/contacts/`       | List/add contacts        |
| GET/POST | `/vendors/{id}/addresses/`      | List/add addresses       |
| GET/POST | `/vendors/{id}/bank-accounts/`  | List/add bank accounts   |
| GET/POST | `/vendors/{id}/products/`       | List/add vendor products |
| GET      | `/vendors/{id}/performance/`    | Performance records      |
| GET/POST | `/vendors/{id}/communications/` | Communication timeline   |
| GET/POST | `/vendors/{id}/documents/`      | Document management      |
| GET      | `/vendors/{id}/history/`        | Change audit trail       |

### Filtering

| Parameter                     | Description                      | Example                     |
| ----------------------------- | -------------------------------- | --------------------------- |
| `status`                      | Exact status match               | `?status=active`            |
| `vendor_type`                 | Exact type match                 | `?vendor_type=manufacturer` |
| `province`                    | Province (case-insensitive)      | `?province=Western`         |
| `district`                    | District (case-insensitive)      | `?district=Colombo`         |
| `is_preferred_vendor`         | Boolean filter                   | `?is_preferred_vendor=true` |
| `rating_min` / `rating_max`   | Rating range                     | `?rating_min=4.0`           |
| `created_from` / `created_to` | Date range                       | `?created_from=2024-01-01`  |
| `search`                      | Multi-field text search          | `?search=electronics`       |
| `ordering`                    | Sort field (prefix `-` for desc) | `?ordering=-rating`         |

### CSV Import Format

Required columns: `company_name`, `vendor_type`

Optional columns: `business_registration`, `tax_id`, `email`, `phone`, `address`, `city`, `district`, `province`, `payment_terms`, `credit_limit`

### Document Upload

- Allowed file types: PDF, DOC, DOCX, JPG, PNG
- Maximum file size: 10 MB
- Document types: `contract`, `certificate`, `price_list`, `license`, `other`

---

## Models

| Model                 | Purpose                             |
| --------------------- | ----------------------------------- |
| `Vendor`              | Core vendor profile with 40+ fields |
| `VendorContact`       | Contact persons per vendor          |
| `VendorBankAccount`   | Bank/payment details                |
| `VendorAddress`       | Multiple addresses per vendor       |
| `VendorProduct`       | Product-vendor link with pricing    |
| `VendorPriceList`     | Tiered pricing lists                |
| `VendorPriceListItem` | Individual items in price lists     |
| `VendorPerformance`   | Period-based performance metrics    |
| `VendorCommunication` | Interaction logging                 |
| `VendorDocument`      | Document file storage               |
| `VendorHistory`       | Field-level change audit trail      |

## Services

| Service                | Purpose                       |
| ---------------------- | ----------------------------- |
| `VendorService`        | Core CRUD + status management |
| `CatalogService`       | Product catalog & pricing     |
| `PerformanceService`   | Metric calculations           |
| `CommunicationService` | Interaction logging           |
| `DocumentService`      | File upload & management      |
| `VendorImportService`  | CSV import with validation    |
| `VendorExportService`  | CSV export                    |
| `VendorHistoryService` | Audit trail tracking          |
