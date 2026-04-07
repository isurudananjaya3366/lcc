# Payment Recording Module

> **Phase:** 05 — ERP Core Modules Part 2  
> **SubPhase:** 07 — Payment Recording  
> **App:** `apps.payments`

## Features

- **Multiple payment methods** — CASH, CARD, BANK_TRANSFER, MOBILE, CHECK, STORE_CREDIT
- **Split payments** — single invoice paid with multiple methods
- **Partial payments & payment plans** — installment-based scheduling
- **Payment receipts** — auto-generated with PDF support
- **Refund processing** — full approval workflow (request → approve → process)
- **Store credit management** — credit-based refunds
- **Payment history & audit trail** — every state change tracked
- **Email notifications** — confirmation, receipt, refund, reminder emails
- **Multi-currency support** — exchange rates and base-currency conversion
- **Sri Lankan context** — LKR default, FriMi / eZ Cash / mCash / Genie mobile providers

## API Endpoints

### Payments

| Method | Endpoint                                   | Description           |
| ------ | ------------------------------------------ | --------------------- |
| GET    | `/api/v1/payments/payments/`               | List payments         |
| POST   | `/api/v1/payments/payments/`               | Create payment        |
| GET    | `/api/v1/payments/payments/{id}/`          | Payment detail        |
| PUT    | `/api/v1/payments/payments/{id}/`          | Update payment        |
| PATCH  | `/api/v1/payments/payments/{id}/`          | Partial update        |
| DELETE | `/api/v1/payments/payments/{id}/`          | Soft-delete (pending) |
| POST   | `/api/v1/payments/payments/{id}/complete/` | Complete payment      |
| POST   | `/api/v1/payments/payments/{id}/cancel/`   | Cancel payment        |
| GET    | `/api/v1/payments/payments/{id}/receipt/`  | Download receipt PDF  |

### Refunds

| Method | Endpoint                                 | Description    |
| ------ | ---------------------------------------- | -------------- |
| GET    | `/api/v1/payments/refunds/`              | List refunds   |
| POST   | `/api/v1/payments/refunds/`              | Request refund |
| GET    | `/api/v1/payments/refunds/{id}/`         | Refund detail  |
| POST   | `/api/v1/payments/refunds/{id}/approve/` | Approve refund |
| POST   | `/api/v1/payments/refunds/{id}/reject/`  | Reject refund  |
| POST   | `/api/v1/payments/refunds/{id}/process/` | Process refund |

### Reports

| Method | Endpoint                                               | Description        |
| ------ | ------------------------------------------------------ | ------------------ |
| GET    | `/api/v1/payments/reports/?report_type=summary`        | Aggregate totals   |
| GET    | `/api/v1/payments/reports/?report_type=daily`          | Daily breakdown    |
| GET    | `/api/v1/payments/reports/?report_type=monthly`        | Monthly breakdown  |
| GET    | `/api/v1/payments/reports/?report_type=reconciliation` | Expected vs actual |
| GET    | `/api/v1/payments/reports/?report_type=analytics`      | Method breakdown   |

### Filtering (query params)

**Payments:** `method`, `status`, `customer`, `customer_name`, `invoice`, `invoice_number`,
`order`, `currency`, `has_receipt`, `refund_status`, `payment_date_from`, `payment_date_to`,
`created_from`, `created_to`, `amount_min`, `amount_max`

**Refunds:** `status`, `reason`, `payment`, `customer`, `refund_method`,
`created_from`, `created_to`, `amount_min`, `amount_max`

## Module Structure

```
apps/payments/
├── models/
│   ├── payment.py              # Payment model
│   ├── payment_allocation.py   # Invoice ↔ Payment allocation
│   ├── payment_history.py      # Audit trail
│   ├── payment_method_config.py# Method configuration
│   ├── payment_plan.py         # Installment plans
│   ├── payment_receipt.py      # Receipt generation
│   ├── payment_sequence.py     # Number generation
│   ├── payment_settings.py     # Late fees / settings
│   ├── refund.py               # Refund model
│   └── split_payment.py        # Split payment components
├── services/
│   ├── payment_service.py      # Payment CRUD + transitions
│   ├── refund_service.py       # Refund workflow
│   ├── receipt_service.py      # Receipt generation
│   ├── receipt_pdf_service.py  # PDF rendering
│   └── email_service.py        # Email notifications
├── serializers/
│   └── payment.py              # All serializers
├── views/
│   ├── payment.py              # PaymentViewSet
│   ├── refund.py               # RefundViewSet
│   └── report_views.py         # PaymentReportView
├── tasks/
│   ├── email_tasks.py          # Celery email tasks
│   └── reminder_tasks.py       # Celery reminder tasks
├── constants.py                # PaymentMethod / PaymentStatus
├── exceptions.py               # PaymentError / RefundError
├── filters.py                  # PaymentFilter / RefundFilter
├── urls.py                     # URL configuration
└── admin.py                    # Admin registration
```

## Sri Lankan Context

**Mobile providers:** FriMi, eZ Cash, mCash, Genie  
**Banks:** Commercial Bank, Sampath, HNB, BOC, NTB, DFCC, NSB  
**Default currency:** LKR

## Running Tests

```bash
docker compose exec -T -e DJANGO_SETTINGS_MODULE=config.settings.test_pg \
  backend python -m pytest tests/payments/ -v
```
