# Quote Management Module

## Overview

The Quote Management module provides a complete quotation lifecycle for the POS system, enabling businesses to create, send, track, and convert quotations to orders.

## Architecture

```
apps/quotes/
├── models/
│   ├── quote.py           # Core Quote model (50+ fields)
│   ├── line_item.py       # QuoteLineItem with pricing
│   ├── history.py         # QuoteHistory audit trail
│   ├── settings.py        # QuoteSettings (per-tenant)
│   ├── template.py        # QuoteTemplate (PDF layout)
│   └── quote_sequence.py  # Auto-incrementing numbers
├── services/
│   ├── quote_service.py          # Business logic & transitions
│   ├── calculation.py            # Financial calculations
│   ├── pdf_generator.py          # PDF generation (reportlab)
│   ├── email_service.py          # Email delivery
│   └── quote_number_generator.py # Sequential numbering
├── views/
│   ├── quote.py    # QuoteViewSet (authenticated API)
│   └── public.py   # Public endpoints (token-based)
├── serializers/
│   ├── quote.py       # Quote list/detail serializers
│   └── line_item.py   # LineItem serializer
├── tasks/
│   └── email.py       # Celery async email tasks
├── signals/
│   └── recalculation.py  # Auto-recalc & history signals
├── filters/
│   └── quote.py       # django-filter FilterSet
├── constants.py       # Status, currency, discount enums
└── urls.py            # URL routing
```

## Key Features

- **Lifecycle Management**: Draft → Sent → Accepted/Rejected/Expired → Converted
- **Financial Calculations**: Line items, discounts (% / fixed), tax, grand total
- **PDF Generation**: Customizable templates with reportlab
- **Email Delivery**: Async via Celery with exponential backoff
- **Public Links**: Token-based customer portal (view, accept, reject)
- **Revision System**: Create new versions of existing quotes
- **Audit History**: Full change tracking with old/new values
- **View Tracking**: Count and timestamp of public views

## Contents

- [API Reference](api.md)
- [Models](models.md)
- [Services](services.md)
- [Configuration](configuration.md)
