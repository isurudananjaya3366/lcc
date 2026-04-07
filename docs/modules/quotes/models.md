# Quote Models

## Quote

The core model representing a quotation.

**Key fields:**

- `id` (UUID, PK) — Auto-generated UUID primary key
- `quote_number` (CharField) — Human-readable sequential number (e.g., QT-2026-00001)
- `status` (CharField) — Current lifecycle status
- `title` (CharField) — Optional quote title
- `issue_date` (DateField) — Date the quote was created
- `valid_until` (DateField) — Expiration date
- `currency` (CharField) — LKR or USD

**Customer fields:**

- `customer` (FK → Customer, optional)
- `guest_name`, `guest_email`, `guest_phone` — For walk-in customers

**Financial fields:**

- `subtotal`, `discount_amount`, `tax_amount`, `total` (DecimalField)
- `discount_type` (PERCENTAGE or FIXED), `discount_value`

**Tracking fields:**

- `view_count` (PositiveIntegerField) — Public view count
- `last_viewed_at` (DateTimeField) — Last public view timestamp
- `email_sent_to`, `email_sent_at`, `email_sent_count`, `email_last_error`
- `sent_at`, `accepted_at`, `rejected_at`, `converted_at`

**Properties:**

- `is_editable` — True if status is in EDITABLE_STATES
- `is_expired` — True if valid_until is past
- `is_locked` — True if status is not draft
- `customer_display_name` — Customer name or guest name
- `days_until_expiry` — Days until valid_until

**Manager methods:**

- `Quote.objects.drafts()` — Filter draft quotes
- `Quote.objects.active()` — Filter non-terminal quotes
- `Quote.objects.expiring_soon(days=7)` — Quotes expiring within N days

## QuoteLineItem

Individual line items within a quote.

**Key fields:**

- `quote` (FK → Quote)
- `product` (FK → Product, optional), `variant` (FK → ProductVariant, optional)
- `product_name`, `custom_description` — Text fallbacks
- `quantity`, `unit_price`, `line_total` (DecimalField)
- `discount_type`, `discount_value`, `discount_amount`
- `is_taxable`, `tax_rate`, `tax_amount`
- `position` (IntegerField) — Display ordering

## QuoteHistory

Audit trail for quote changes.

**Event types:** CREATED, UPDATED, STATUS_CHANGED, SENT, ACCEPTED, REJECTED, EXPIRED, CONVERTED, DUPLICATED, REVISION_CREATED

## QuoteTemplate

PDF template configuration (per-tenant).

**Key fields:** `name`, `primary_color`, `page_size`, `page_orientation`, `margins`, `layout_options`

## QuoteSettings

Per-tenant quote configuration.

**Key fields:** `default_currency`, `default_validity_days`, `auto_numbering`, `number_prefix`

## QuoteSequence

Auto-incrementing sequence for quote numbers.
