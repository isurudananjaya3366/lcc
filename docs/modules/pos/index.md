# POS Module

The Point of Sale (POS) module provides a complete retail terminal solution
integrated into the ERP platform. It handles product lookup, cart management,
multi-method payment processing, session/shift management, and cash
reconciliation — all within a multi-tenant Django architecture.

## Key Features

- **Terminal Management** — register, configure, and monitor POS hardware
- **Session / Shift Lifecycle** — open, suspend, resume, close with cash reconciliation
- **Cart Operations** — add items, update quantities, apply line & cart discounts
- **Product Search** — barcode scanning, SKU lookup, name search, combined search
- **Multi-Method Payments** — cash, card, mobile (FriMi/Genie), store credit, split
- **Transaction Completion** — atomic stock / session-total updates, receipt generation
- **Quick Buttons** — configurable product shortcuts per terminal

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│  Frontend (Next.js)                                 │
└────────────────┬────────────────────────────────────┘
                 │ REST / JSON
┌────────────────▼────────────────────────────────────┐
│  DRF Views / ViewSets                               │
│  terminal · cart · search · payment                 │
├─────────────────────────────────────────────────────┤
│  Services Layer                                      │
│  CartService · PaymentService · ProductSearchService │
├─────────────────────────────────────────────────────┤
│  Models (Django ORM)                                 │
│  POSTerminal · POSSession · POSCart · POSCartItem    │
│  POSPayment · SearchHistory · QuickButtonGroup       │
├─────────────────────────────────────────────────────┤
│  Database (PostgreSQL per tenant)                    │
└─────────────────────────────────────────────────────┘
```

## Quick Links

| Topic                          | Document                                 |
| ------------------------------ | ---------------------------------------- |
| Architecture & design patterns | [architecture.md](architecture.md)       |
| Terminals & sessions           | [terminal.md](terminal.md)               |
| Cart & items                   | [cart.md](cart.md)                       |
| Product search                 | [search.md](search.md)                   |
| Payment processing             | [payment.md](payment.md)                 |
| Transaction lifecycle          | [transaction.md](transaction.md)         |
| REST API reference             | [api.md](api.md)                         |
| Configuration & settings       | [configuration.md](configuration.md)     |
| Module integrations            | [integration.md](integration.md)         |
| Troubleshooting                | [troubleshooting.md](troubleshooting.md) |

## Module Location

```
backend/apps/pos/
├── constants.py          # Enums & choices
├── urls.py               # Router + URL patterns
├── terminal/             # POSTerminal, POSSession
├── cart/                 # POSCart, POSCartItem, CartService
├── search/               # ProductSearchService, QuickButtons
└── payment/              # POSPayment, PaymentService
```
