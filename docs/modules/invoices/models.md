# Invoice Module — Model Reference

## Invoice Model

The `Invoice` model (`apps.invoices.models.invoice`) stores all invoice types: STANDARD, SVAT, CREDIT_NOTE, and DEBIT_NOTE.

### Key Fields

| Field                               | Type         | Description                                         |
| ----------------------------------- | ------------ | --------------------------------------------------- |
| `id`                                | UUIDField    | Primary key (from UUIDMixin)                        |
| `invoice_number`                    | CharField    | Unique generated number (INV/SVAT/CN/DN prefix)     |
| `type`                              | CharField    | STANDARD, SVAT, CREDIT_NOTE, DEBIT_NOTE             |
| `status`                            | CharField    | DRAFT → ISSUED → SENT → PAID (see workflows.md)     |
| `customer`                          | FK(Customer) | Customer reference (PROTECT)                        |
| `order`                             | FK(Order)    | Source order reference (SET_NULL)                   |
| `related_invoice`                   | FK(Invoice)  | For credit/debit notes → original invoice (PROTECT) |
| `customer_name/email/phone/address` | CharField    | Denormalized customer details                       |
| `customer_tax_id`                   | CharField    | Customer's tax identification                       |
| `business_name/address/phone/email` | CharField    | Business details                                    |
| `issue_date`                        | DateField    | When invoice was issued                             |
| `due_date`                          | DateField    | Payment due date                                    |
| `sent_date`                         | DateField    | When email was sent                                 |
| `paid_date`                         | DateField    | When fully paid                                     |
| `payment_terms`                     | IntegerField | Days until due (default: 30)                        |
| `subtotal`                          | DecimalField | Sum of line item totals                             |
| `discount_amount`                   | DecimalField | Header-level discount                               |
| `tax_amount`                        | DecimalField | Total tax                                           |
| `total`                             | DecimalField | Final total                                         |
| `amount_paid`                       | DecimalField | Amount received                                     |
| `balance_due`                       | DecimalField | Remaining balance                                   |
| `currency`                          | CharField    | LKR or USD                                          |
| `tax_scheme`                        | CharField    | VAT, SVAT, NONE, EXEMPT                             |
| `pdf_file`                          | FileField    | Generated PDF                                       |
| `pdf_version`                       | IntegerField | Increments on regeneration                          |

### Custom Manager

`InvoiceManager` provides:

- `active()` — excludes soft-deleted
- `drafts()`, `issued()`, `overdue()`, `paid()` — status filters
- `get_default()` — raises DoesNotExist

## InvoiceLineItem Model

| Field             | Type         | Description              |
| ----------------- | ------------ | ------------------------ |
| `invoice`         | FK(Invoice)  | Parent invoice (CASCADE) |
| `position`        | IntegerField | Display order            |
| `product`         | FK(Product)  | Optional product link    |
| `description`     | TextField    | Line item description    |
| `quantity`        | DecimalField | Quantity                 |
| `unit_price`      | DecimalField | Price per unit           |
| `tax_rate`        | DecimalField | Tax percentage           |
| `tax_amount`      | DecimalField | Calculated tax           |
| `line_total`      | DecimalField | Calculated total         |
| `hsn_code`        | CharField    | HSN/SAC tax code         |
| `hsn_description` | CharField    | HSN description          |

## InvoiceHistory Model

Audit trail for all invoice state changes.

| Field        | Type        | Description                                   |
| ------------ | ----------- | --------------------------------------------- |
| `invoice`    | FK(Invoice) | Invoice reference                             |
| `action`     | CharField   | CREATED, ISSUED, SENT, PAYMENT_RECORDED, etc. |
| `old_status` | CharField   | Previous status                               |
| `new_status` | CharField   | New status                                    |
| `user`       | FK(User)    | Who performed the action                      |
| `notes`      | TextField   | Additional context                            |
| `metadata`   | JSONField   | Extra structured data                         |

### Indexes

- `invoice` — fast lookup by invoice
- `action` — filter by action type
- `created_on` — chronological queries

## InvoiceSettings Model

Per-tenant invoice configuration (OneToOne with Tenant).

| Field                   | Description                       |
| ----------------------- | --------------------------------- |
| `invoice_prefix`        | Default: "INV"                    |
| `credit_note_prefix`    | Default: "CN"                     |
| `debit_note_prefix`     | Default: "DN"                     |
| `default_due_days`      | Default: 30                       |
| `default_vat_rate`      | Default: 12.00                    |
| `auto_send_on_issue`    | Auto-email when issued            |
| `auto_issue_from_order` | Auto-create from completed orders |

## InvoiceTemplate Model

Per-tenant PDF customization (OneToOne with Tenant).

Includes: logo, business info, colors, fonts, page layout, bank details, footer text, display toggles.
