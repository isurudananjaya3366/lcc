# Invoice Module

## Overview

The Invoice Module provides comprehensive invoicing capabilities for the LankaCommerce Cloud POS system, including standard invoices, SVAT invoices, credit notes, and debit notes with full Sri Lanka tax compliance.

## Key Features

- **Multi-type invoicing**: Standard, SVAT, Credit Note, Debit Note
- **Full lifecycle management**: Draft → Issued → Sent → Paid (with partial payments)
- **Sri Lanka tax compliance**: VAT, SVAT, BRN support
- **PDF generation**: Customizable templates with WeasyPrint
- **Email delivery**: Automated invoice, reminder, and overdue emails via Celery
- **Credit/Debit notes**: Linked adjustment documents with credit limit validation
- **Aging reports**: Accounts receivable aging analysis
- **Multi-currency**: LKR, USD, EUR, GBP with exchange rates

## Invoice Lifecycle

```
DRAFT → ISSUED → SENT → PARTIAL → PAID
                ↓         ↓
              OVERDUE    OVERDUE
                ↓
DRAFT → CANCELLED
ISSUED/SENT → VOID
```

## Models

| Model           | Purpose                                 |
| --------------- | --------------------------------------- |
| Invoice         | Core invoice record (~50 fields)        |
| InvoiceLineItem | Line items with pricing, tax, discounts |
| InvoiceHistory  | Audit trail for all changes             |
| InvoiceSettings | Per-tenant configuration                |
| InvoiceTemplate | PDF template customization              |

## API Endpoints

| Method    | Path                              | Description              |
| --------- | --------------------------------- | ------------------------ |
| GET       | /api/v1/invoices/                 | List invoices            |
| POST      | /api/v1/invoices/                 | Create invoice           |
| GET       | /api/v1/invoices/{id}/            | Invoice detail           |
| PUT/PATCH | /api/v1/invoices/{id}/            | Update invoice           |
| DELETE    | /api/v1/invoices/{id}/            | Soft delete (draft only) |
| POST      | /api/v1/invoices/{id}/issue/      | Issue invoice            |
| POST      | /api/v1/invoices/{id}/send/       | Send via email           |
| POST      | /api/v1/invoices/{id}/mark-paid/  | Record payment           |
| POST      | /api/v1/invoices/{id}/cancel/     | Cancel                   |
| POST      | /api/v1/invoices/{id}/void/       | Void                     |
| POST      | /api/v1/invoices/{id}/duplicate/  | Duplicate                |
| GET       | /api/v1/invoices/{id}/pdf/        | Download PDF             |
| GET       | /api/v1/invoices/{id}/preview/    | HTML preview             |
| GET       | /api/v1/invoices/{id}/history/    | Audit history            |
| GET/POST  | /api/v1/invoices/{id}/line-items/ | Line items               |
| POST      | /api/v1/invoices/credit-note/     | Create credit note       |
| POST      | /api/v1/invoices/debit-note/      | Create debit note        |
| GET       | /api/v1/invoices/aging-report/    | Aging report             |

## Services

| Service                   | Purpose                                |
| ------------------------- | -------------------------------------- |
| InvoiceService            | Core CRUD and status transitions       |
| InvoiceCalculationService | Financial calculations and tax         |
| InvoiceNumberGenerator    | Sequential number generation           |
| CreditNoteService         | Credit note creation and application   |
| DebitNoteService          | Debit note creation and application    |
| InvoiceBalanceService     | Balance recalculation with adjustments |
| InvoicePDFGenerator       | HTML-to-PDF generation                 |
| InvoiceEmailService       | Email sending with PDF attachments     |
