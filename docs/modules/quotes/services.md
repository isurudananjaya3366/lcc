# Quote Services

## QuoteService

Core business logic for quote lifecycle management. All methods are `@classmethod` or `@staticmethod`.

### Status Transitions

```python
QuoteService.send_quote(quote, user=None)      # draft → sent
QuoteService.accept_quote(quote, user=None)     # sent → accepted
QuoteService.reject_quote(quote, reason="", user=None)  # sent → rejected
QuoteService.expire_quote(quote, user=None)     # sent → expired
QuoteService.convert_to_order(quote, user=None) # accepted → converted
```

### CRUD Operations

```python
QuoteService.duplicate_quote(quote, user=None)  # Clone quote as new draft
QuoteService.create_revision(quote, user=None)  # Create revision of existing quote
```

### Query Helpers

```python
QuoteService.get_available_actions(quote)           # Returns list of action name strings
QuoteService.get_available_actions_detailed(quote)   # Returns list of action dicts for API
QuoteService.get_quote_history(quote)               # Returns history queryset
QuoteService.get_recent_history(quote, limit=10)    # Returns recent history
```

### Bulk Operations

```python
QuoteService.bulk_expire_quotes()      # Expire all past-due sent quotes
QuoteService.check_and_expire_quote(quote)  # Check and expire single quote
```

---

## QuoteCalculationService

Financial calculation engine. Instance-based — pass quote in constructor.

```python
svc = QuoteCalculationService(quote)
svc.calculate_all(save=True)        # Full pipeline
svc.calculate_line_totals()         # Recalculate each line item
svc.calculate_subtotal()            # Sum line totals
svc.apply_header_discount()         # Apply quote-level discount
svc.calculate_tax()                 # Sum tax amounts
svc.calculate_grand_total()         # Compute final total
svc.get_total_breakdown()           # Return full financial breakdown dict
```

---

## QuoteEmailService

Email delivery for quotes. All methods are `@staticmethod`.

```python
QuoteEmailService.send_quote_email(quote, to_email=None, cc=None, subject=None, message=None)
QuoteEmailService.send_expiry_reminder(quote, to_email=None)
```

---

## QuotePDFGenerator

PDF generation using reportlab. Instance-based.

```python
gen = QuotePDFGenerator(quote, template=None)
pdf_bytes = gen.generate()          # Returns raw PDF bytes
file_path = gen.generate_and_save() # Saves to quote.pdf_file
```

---

## QuoteNumberGenerator

Sequential quote number generation.

```python
number = QuoteNumberGenerator.generate()  # e.g., "QT-2026-00001"
```
