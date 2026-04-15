# CRM Module — Frontend Documentation

## Overview

The CRM (Customer Relationship Management) module provides comprehensive customer, vendor, and purchase order management within the ERP dashboard. Built with Next.js App Router, React Hook Form, TanStack Query, and shadcn/ui.

## Module Structure

```
app/(dashboard)/
├── customers/
│   ├── page.tsx              # Customer list page
│   ├── loading.tsx           # List skeleton
│   ├── error.tsx             # Error boundary
│   ├── new/
│   │   ├── page.tsx          # Create customer page
│   │   └── error.tsx         # Error boundary
│   └── [id]/
│       ├── page.tsx          # Customer detail page
│       ├── loading.tsx       # Detail skeleton
│       └── error.tsx         # Error boundary
├── vendors/
│   ├── page.tsx
│   ├── loading.tsx
│   ├── error.tsx
│   ├── new/
│   │   ├── page.tsx
│   │   └── error.tsx
│   └── [id]/
│       ├── page.tsx
│       ├── loading.tsx
│       └── error.tsx
└── purchase-orders/
    ├── page.tsx
    ├── loading.tsx
    ├── error.tsx
    ├── new/
    │   ├── page.tsx
    │   └── error.tsx
    └── [id]/
        ├── page.tsx
        ├── loading.tsx
        └── error.tsx
```

## Components

### Customer Components

| Component               | Path                                                 | Description                                                   |
| ----------------------- | ---------------------------------------------------- | ------------------------------------------------------------- |
| `CustomersList`         | `components/modules/crm/Customers/CustomersList.tsx` | Main list view with header, summary cards, filters, and table |
| `CustomersHeader`       | `Customers/CustomersHeader.tsx`                      | Page title, search, import/export buttons                     |
| `CustomerSummaryCards`  | `Customers/CustomerSummaryCards.tsx`                 | KPI cards: total, active, credit outstanding                  |
| `CustomerFilters`       | `Customers/CustomerFilters.tsx`                      | Status, type, and search filters                              |
| `CustomersTable`        | `Customers/CustomersTable.tsx`                       | Data table with sorting and pagination                        |
| `CustomerActionsCell`   | `Customers/CustomerActionsCell.tsx`                  | Row actions dropdown (view, edit, delete)                     |
| `CustomerDetails`       | `Customers/CustomerDetails.tsx`                      | Detail page container with profile components                 |
| `CustomerForm`          | `Customers/CustomerForm.tsx`                         | Create customer form with validation                          |
| `CustomerContactFields` | `Customers/CustomerContactFields.tsx`                | Phone, mobile, email, tax ID form fields                      |
| `CustomerAddressFields` | `Customers/CustomerAddressFields.tsx`                | Street, city, district, postal code, country                  |

### Customer Profile Components

| Component            | Path                                     | Description                                                |
| -------------------- | ---------------------------------------- | ---------------------------------------------------------- |
| `CustomerHeader`     | `CustomerProfile/CustomerHeader.tsx`     | Avatar, name, status badge, actions                        |
| `CustomerAvatar`     | `CustomerProfile/CustomerAvatar.tsx`     | Customer avatar with initials fallback                     |
| `CustomerQuickStats` | `CustomerProfile/CustomerQuickStats.tsx` | Orders, spent, avg order value stats                       |
| `ContactInfoCard`    | `CustomerProfile/ContactInfoCard.tsx`    | Phone, email, address display                              |
| `CreditInfoCard`     | `CustomerProfile/CreditInfoCard.tsx`     | Credit limit, balance, available credit                    |
| `CustomerTabs`       | `CustomerProfile/CustomerTabs.tsx`       | URL-synced tabs: Overview, Orders, Invoices, Communication |
| `OverviewTab`        | `CustomerProfile/OverviewTab.tsx`        | Recent orders, activity summary                            |
| `OrdersTab`          | `CustomerProfile/OrdersTab.tsx`          | Customer order history table                               |
| `InvoicesTab`        | `CustomerProfile/InvoicesTab.tsx`        | Customer invoice list                                      |
| `CommunicationTab`   | `CustomerProfile/CommunicationTab.tsx`   | Communication timeline + add form                          |
| `EditCustomerModal`  | `CustomerProfile/EditCustomerModal.tsx`  | Edit customer details modal                                |
| `AdjustCreditModal`  | `CustomerProfile/AdjustCreditModal.tsx`  | Adjust credit limit modal                                  |

### Vendor Components

| Component             | Path                              | Description                          |
| --------------------- | --------------------------------- | ------------------------------------ |
| `VendorsList`         | `Vendors/VendorsList.tsx`         | Main list view                       |
| `VendorsHeader`       | `Vendors/VendorsHeader.tsx`       | Title, search, import/export buttons |
| `VendorSummaryCards`  | `Vendors/VendorSummaryCards.tsx`  | KPI cards                            |
| `VendorFilters`       | `Vendors/VendorFilters.tsx`       | Status, type, category filters       |
| `VendorsTable`        | `Vendors/VendorsTable.tsx`        | Data table with sorting              |
| `VendorActionsCell`   | `Vendors/VendorActionsCell.tsx`   | Row actions dropdown                 |
| `VendorDetails`       | `Vendors/VendorDetails.tsx`       | Detail page container                |
| `VendorForm`          | `Vendors/VendorForm.tsx`          | Create vendor form with validation   |
| `VendorContactFields` | `Vendors/VendorContactFields.tsx` | Contact form fields                  |
| `VendorTermsFields`   | `Vendors/VendorTermsFields.tsx`   | Payment terms, currency, lead time   |

### Vendor Profile Components

| Component      | Path                             | Description                   |
| -------------- | -------------------------------- | ----------------------------- |
| `VendorHeader` | `VendorProfile/VendorHeader.tsx` | Company name, status, actions |
| `OverviewTab`  | `VendorProfile/OverviewTab.tsx`  | Vendor overview               |
| `ProductsTab`  | `VendorProfile/ProductsTab.tsx`  | Vendor products list          |
| `POHistoryTab` | `VendorProfile/POHistoryTab.tsx` | Purchase order history        |
| `VendorTabs`   | `VendorProfile/VendorTabs.tsx`   | URL-synced tabs               |

### Purchase Order Components

| Component           | Path                                   | Description                                         |
| ------------------- | -------------------------------------- | --------------------------------------------------- |
| `POList`            | `PurchaseOrders/POList.tsx`            | Main PO list view                                   |
| `POHeader`          | `PurchaseOrders/POHeader.tsx`          | Title, create PO button                             |
| `POSummaryCards`    | `PurchaseOrders/POSummaryCards.tsx`    | KPI cards                                           |
| `POFilters`         | `PurchaseOrders/POFilters.tsx`         | Status, vendor, date range filters                  |
| `POTable`           | `PurchaseOrders/POTable.tsx`           | Data table with sorting                             |
| `POActionsCell`     | `PurchaseOrders/POActionsCell.tsx`     | Row actions with cancel dialog                      |
| `PODetails`         | `PurchaseOrders/PODetails.tsx`         | PO detail page with timeline, items, receive button |
| `POForm`            | `PurchaseOrders/POForm.tsx`            | Create PO form with line item editor                |
| `POLineItemEditor`  | `PurchaseOrders/POLineItemEditor.tsx`  | Dynamic add/remove line items                       |
| `POLineItemsTable`  | `PurchaseOrders/POLineItemsTable.tsx`  | Line items with subtotal/tax/shipping footer        |
| `POStatusTimeline`  | `PurchaseOrders/POStatusTimeline.tsx`  | Step-by-step progress dots                          |
| `ReceiveItemsModal` | `PurchaseOrders/ReceiveItemsModal.tsx` | Receive items into inventory modal                  |

### Shared Components

| Component      | Path                      | Description                                                       |
| -------------- | ------------------------- | ----------------------------------------------------------------- |
| `ImportDialog` | `shared/ImportDialog.tsx` | Multi-step CSV import: upload → column mapping → preview → import |
| `ExportButton` | `shared/ExportButton.tsx` | CSV export with date-stamped filename                             |

## Hooks

| Hook                      | File                             | Description                   |
| ------------------------- | -------------------------------- | ----------------------------- |
| `useCustomers`            | `hooks/crm/useCustomers.ts`      | Paginated customer list query |
| `useCustomer`             | `hooks/crm/useCustomers.ts`      | Single customer detail query  |
| `useCreateCustomer`       | `hooks/crm/useCustomers.ts`      | Create customer mutation      |
| `useUpdateCustomer`       | `hooks/crm/useCustomers.ts`      | Update customer mutation      |
| `useDeleteCustomer`       | `hooks/crm/useCustomers.ts`      | Delete customer mutation      |
| `useAdjustCredit`         | `hooks/crm/useCustomers.ts`      | Adjust credit limit mutation  |
| `useVendors`              | `hooks/crm/useVendors.ts`        | Paginated vendor list query   |
| `useVendor`               | `hooks/crm/useVendors.ts`        | Single vendor detail query    |
| `useCreateVendor`         | `hooks/crm/useVendors.ts`        | Create vendor mutation        |
| `useUpdateVendor`         | `hooks/crm/useVendors.ts`        | Update vendor mutation        |
| `useDeleteVendor`         | `hooks/crm/useVendors.ts`        | Delete vendor mutation        |
| `useVendorProducts`       | `hooks/crm/useVendors.ts`        | Vendor products query         |
| `useVendorPOs`            | `hooks/crm/useVendors.ts`        | Vendor PO history query       |
| `usePurchaseOrders`       | `hooks/crm/usePurchaseOrders.ts` | Paginated PO list query       |
| `usePurchaseOrder`        | `hooks/crm/usePurchaseOrders.ts` | Single PO detail query        |
| `useCreatePurchaseOrder`  | `hooks/crm/usePurchaseOrders.ts` | Create PO mutation            |
| `useUpdatePurchaseOrder`  | `hooks/crm/usePurchaseOrders.ts` | Update PO mutation            |
| `useCancelPurchaseOrder`  | `hooks/crm/usePurchaseOrders.ts` | Cancel PO mutation            |
| `useReceivePurchaseOrder` | `hooks/crm/usePurchaseOrders.ts` | Receive items mutation        |

## Validation Schemas

| Schema               | File                               | Description                                                                          |
| -------------------- | ---------------------------------- | ------------------------------------------------------------------------------------ |
| `customerFormSchema` | `lib/validations/customer.ts`      | Customer type, name, contact, address, credit fields with SL phone/postal validation |
| `vendorFormSchema`   | `lib/validations/vendor.ts`        | Company info, contact, address, payment terms, currency with SL phone validation     |
| `poFormSchema`       | `lib/validations/purchaseOrder.ts` | Vendor, dates, line items (min 1), costs, notes/terms                                |

## Query Keys

Defined in `lib/queryKeys.ts`:

- `customerKeys` — `all`, `lists()`, `list(params)`, `details()`, `detail(id)`
- `vendorKeys` — same pattern
- `purchaseOrderKeys` — same pattern with `POFilters` interface

## Services

| Service           | File                              | Key Methods                            |
| ----------------- | --------------------------------- | -------------------------------------- |
| `customerService` | `services/api/customerService.ts` | CRUD, credit adjust, import/export CSV |
| `vendorService`   | `services/api/vendorService.ts`   | CRUD, PO management, import/export CSV |

## Metadata

All CRM pages use `createCRMMetadata(title, description)` from `lib/metadata/crm.ts` which generates consistent SEO metadata including Open Graph and Twitter cards.

## Patterns

### List Pages

Header → Summary Cards → Filters → Table with sorting/pagination

### Detail Pages

Wrapped in `<Suspense>` with skeleton fallback. Header with status badge → tabbed content (URL-synced via searchParams).

### Forms

React Hook Form + Zod schema + zodResolver. Sub-components for field groups (ContactFields, AddressFields, TermsFields). Mutations via TanStack Query with cache invalidation.

### Import/Export

CSV-based. Import flow: Upload → Column Mapping (auto-matched by header name) → Preview (first 5 rows) → Import with results. Export downloads blob as date-stamped CSV.

### Error Boundaries

All routes have `error.tsx` with AlertTriangle icon, error message, and retry button.

## Currency

All monetary values displayed in Sri Lankan Rupees (₨) using `en-LK` locale formatting.
