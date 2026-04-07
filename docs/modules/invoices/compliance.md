# Invoice Module — Sri Lankan Tax Compliance

## VAT (Value Added Tax)

- **Standard VAT Rate:** 12% (as of 2024)
- **Constant:** `SRI_LANKA_VAT_RATE = Decimal("12.00")` in `apps/invoices/constants.py`
- **Applied to:** All taxable goods and services
- **Tax Scheme:** `"VAT"` on the Invoice model

### VAT Calculation

```
tax_amount = (unit_price × quantity - discount) × (vat_rate / 100)
line_total = (unit_price × quantity - discount) + tax_amount
```

### Required Fields for VAT Invoices

- Business Registration Number (BRN)
- VAT Registration Number
- Customer Tax ID (if B2B)
- HSN/SAC codes for line items

## SVAT (Simplified VAT)

- **SVAT Rate:** 0% (zero-rated for SVAT-eligible suppliers)
- **Constant:** `SRI_LANKA_SVAT_RATE = Decimal("0.00")` in `apps/invoices/constants.py`
- **Applied to:** Transactions eligible for SVAT scheme
- **Tax Scheme:** `"SVAT"` on the Invoice model

### SVAT Requirements

- SVAT registration number must be present on invoice
- Buyer must be SVAT-registered
- Invoice must clearly indicate SVAT status
- Zero tax amount on all line items

## Invoice Number Formats

| Type        | Prefix | Format                | Example         |
| ----------- | ------ | --------------------- | --------------- |
| Standard    | INV    | INV-{YEAR}-{SEQ:05d}  | INV-2026-00001  |
| SVAT        | SVAT   | SVAT-{YEAR}-{SEQ:05d} | SVAT-2026-00001 |
| Credit Note | CN     | CN-{YEAR}-{SEQ:05d}   | CN-2026-00001   |
| Debit Note  | DN     | DN-{YEAR}-{SEQ:05d}   | DN-2026-00001   |

Sequences reset annually and are unique per type within each tenant.

## Credit Notes & Debit Notes

### Credit Note Compliance

- Must reference original invoice number
- Total credits cannot exceed original invoice amount minus payments
- Must include valid reason code (RETURN, OVERCHARGE, DISCOUNT, DAMAGED, GOODWILL, ERROR, PARTIAL_REFUND, CANCELLED_ORDER, OTHER)

### Debit Note Compliance

- Must reference original invoice number
- Must include valid reason code (UNDERCHARGE, ADDITIONAL_CHARGE, INTEREST, SHIPPING, ADJUSTMENT, PENALTY, HANDLING, SERVICES, OTHER)
- Increases customer outstanding balance

## Currency

- **Primary:** LKR (Sri Lankan Rupee)
- **Secondary:** USD (for international transactions)
- Exchange rate tracked per invoice for multi-currency support
