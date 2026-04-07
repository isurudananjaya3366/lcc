# Invoice Module — PDF Generation

## Overview

PDF generation uses **WeasyPrint** to convert Django HTML templates to PDF format. The `InvoicePDFGenerator` service manages rendering and storage.

## Template Structure

```
templates/invoices/pdf/
├── invoice.html         # Standard & SVAT invoices
├── credit_note.html     # Credit note layout
├── debit_note.html      # Debit note layout
└── sections/
    ├── header.html      # Company logo, invoice number, dates
    ├── billing.html     # Customer billing details
    ├── line_items.html  # Line items table
    ├── tax_summary.html # Totals and tax breakdown
    └── footer.html      # Payment instructions, terms, bank details
```

## Customization via InvoiceTemplate

Each tenant has an `InvoiceTemplate` model with customizable fields:

| Category          | Fields                                                               |
| ----------------- | -------------------------------------------------------------------- |
| **Branding**      | logo, primary_color, secondary_color, accent_color                   |
| **Business Info** | business_name, business_address, phone, email, website               |
| **Typography**    | header_font, body_font, font_size                                    |
| **Layout**        | page_size (A4/Letter), orientation, margins                          |
| **Bank Details**  | bank_name, account_number, branch, SWIFT code                        |
| **Display**       | show_logo, show_tax_breakdown, show_payment_instructions, show_terms |
| **Footer**        | footer_text, custom_css                                              |

## Service Methods

```python
from apps.invoices.services.pdf_generator import InvoicePDFGenerator

# Full PDF generation (stores on model)
pdf_bytes = InvoicePDFGenerator.generate_pdf(invoice_id)

# HTML preview (no PDF conversion)
html = InvoicePDFGenerator.render_preview(invoice_id)

# Individual section rendering
header_html = InvoicePDFGenerator.render_header(invoice, template)
billing_html = InvoicePDFGenerator.render_billing(invoice)
items_html = InvoicePDFGenerator.render_line_items(invoice)
tax_html = InvoicePDFGenerator.render_tax_summary(invoice)
footer_html = InvoicePDFGenerator.render_footer(invoice, template)
```

## PDF Version Tracking

Each call to `generate_pdf()` increments `pdf_version` and updates `pdf_generated_at` on the Invoice model, enabling audit trails of PDF regeneration.

## Dependencies

- **WeasyPrint** — HTML to PDF conversion (required)
- **Django Template Engine** — HTML rendering
