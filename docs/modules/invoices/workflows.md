# Invoice Module — Workflows

## Invoice Lifecycle

```
DRAFT → ISSUED → SENT → PAID
  │        │       │
  │        │       └─→ PARTIAL → PAID
  │        │       └─→ OVERDUE → PAID
  │        └─→ VOID
  └─→ CANCELLED
```

### Status Transitions

| From    | To        | Trigger                           | Notes                      |
| ------- | --------- | --------------------------------- | -------------------------- |
| DRAFT   | ISSUED    | `InvoiceService.issue_invoice()`  | Assigns number, sets dates |
| DRAFT   | CANCELLED | `InvoiceService.cancel_invoice()` | Requires reason            |
| ISSUED  | SENT      | `InvoiceService.send_invoice()`   | After email delivery       |
| ISSUED  | PAID      | `InvoiceService.mark_paid()`      | Full payment               |
| ISSUED  | PARTIAL   | `InvoiceService.mark_paid()`      | Partial payment            |
| ISSUED  | VOID      | `InvoiceService.void_invoice()`   | Requires reason            |
| SENT    | PAID      | `InvoiceService.mark_paid()`      | Full payment               |
| SENT    | PARTIAL   | `InvoiceService.mark_paid()`      | Partial payment            |
| SENT    | OVERDUE   | Celery task (daily)               | Due date passed            |
| SENT    | VOID      | `InvoiceService.void_invoice()`   | Requires reason            |
| PARTIAL | PAID      | `InvoiceService.mark_paid()`      | Remaining balance paid     |
| OVERDUE | PAID      | `InvoiceService.mark_paid()`      | Late payment received      |

## Order-to-Invoice Flow

1. Order completed → `InvoiceService.create_from_order(order_id)`
2. Invoice created as DRAFT with line items copied
3. Review and adjust if needed
4. Issue → Send → Collect payment

## Credit Note Flow

1. Identify need for credit (return, overcharge, etc.)
2. `CreditNoteService.create_credit_note(invoice_id, reason, ...)`
3. Credit note created with ISSUED status and invoice number
4. Original invoice balance reduced automatically

## Debit Note Flow

1. Identify additional charges
2. `DebitNoteService.create_debit_note(invoice_id, reason, amount=...)`
3. Debit note created with ISSUED status and invoice number
4. Original invoice balance increased

## Overdue Management

A Celery beat task (`check_overdue_invoices`) runs daily:

1. Iterates all active tenants
2. Finds invoices past due date with open balance
3. Marks them as OVERDUE
4. Optionally triggers overdue reminder emails

## Aging Report

`InvoiceService.get_aging_report()` returns outstanding amounts in buckets:

- **current** — not yet due
- **30_days** — 1-30 days overdue
- **60_days** — 31-60 days overdue
- **90_days** — 61-90 days overdue
- **90_plus** — 90+ days overdue
