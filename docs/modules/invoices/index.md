# Invoice Module Documentation

> **Phase:** 05 — ERP Core Modules Part 2  
> **SubPhase:** 06 — Invoice System

---

## Overview

The Invoice module provides comprehensive invoicing capabilities for the POS/ERP system, including:

- Standard invoices and SVAT invoices
- Credit notes and debit notes
- Sri Lankan tax compliance (VAT at 12%, SVAT zero-rated)
- PDF generation with customizable templates
- Email delivery with PDF attachments
- Aging reports and overdue management

## Module Structure

```
apps/invoices/
├── models/
│   ├── invoice.py          # Invoice model (all types)
│   ├── invoice_line_item.py # Line items
│   ├── history.py          # Audit trail
│   ├── invoice_settings.py # Per-tenant settings
│   └── invoice_template.py # PDF template config
├── services/
│   ├── invoice_service.py       # Core business logic
│   ├── calculation_service.py   # Tax & total calculations
│   ├── credit_note_service.py   # Credit note operations
│   ├── debit_note_service.py    # Debit note operations
│   ├── balance_service.py       # Balance recalculation
│   ├── number_generator.py      # Invoice number sequencing
│   ├── pdf_generator.py         # PDF generation (WeasyPrint)
│   └── email_service.py         # Email delivery
├── serializers/                 # DRF serializers
├── views/                       # DRF viewsets
├── filters.py                   # django-filter filters
├── tasks/                       # Celery async tasks
├── signals/                     # Recalculation signals
├── admin.py                     # Django admin
└── urls.py                      # API URL routing
```

## Documentation Index

| Document                                 | Description                                                      |
| ---------------------------------------- | ---------------------------------------------------------------- |
| [models.md](models.md)                   | Model reference (Invoice, LineItem, History, Settings, Template) |
| [api.md](api.md)                         | REST API endpoints, request/response examples                    |
| [compliance.md](compliance.md)           | Sri Lankan VAT/SVAT compliance details                           |
| [pdf-generation.md](pdf-generation.md)   | PDF template customization guide                                 |
| [workflows.md](workflows.md)             | Common invoice workflows and state transitions                   |
| [troubleshooting.md](troubleshooting.md) | Common issues and solutions                                      |

## Quick Start

### Create an Invoice

```python
from apps.invoices.services.invoice_service import InvoiceService

invoice = InvoiceService.create_invoice(
    data={
        "type": "STANDARD",
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "business_name": "My Business",
        "currency": "LKR",
    },
    line_items_data=[
        {"description": "Product A", "quantity": 2, "unit_price": "1000.00"},
    ],
    user=request.user,
)
```

### Issue & Send

```python
InvoiceService.issue_invoice(invoice.id, user=request.user)
InvoiceEmailService.send_invoice_email(invoice.id)
```
