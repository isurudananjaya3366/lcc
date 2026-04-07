# Invoice Module — Troubleshooting

## Common Issues

### "Cannot transition from X to Y"

**Cause:** Attempted an invalid status transition.  
**Solution:** Check allowed transitions in `apps/invoices/constants.py` `ALLOWED_TRANSITIONS`. Use `invoice.get_available_transitions()` to see valid next states.

### "Cannot issue an invoice with no line items"

**Cause:** Tried to issue an invoice that has no line items.  
**Solution:** Add at least one line item before issuing.

### Invoice number not generated

**Cause:** Invoice is still in DRAFT status.  
**Solution:** Invoice numbers are assigned when transitioning to ISSUED via `InvoiceService.issue_invoice()`.

### PDF generation fails with RuntimeError

**Cause:** WeasyPrint is not installed.  
**Solution:** Install with `pip install weasyprint`. WeasyPrint also requires system dependencies (cairo, pango, etc.).

### Email sending fails

**Cause:** Email backend not configured or SMTP credentials invalid.  
**Solution:** Check `DEFAULT_FROM_EMAIL`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` in Django settings.

### Credit note exceeds limit

**Cause:** Total credit notes for an invoice exceed the original total minus payments.  
**Solution:** Check outstanding creditable amount: `original.total - original.amount_paid - applied_credits - pending_credits`.

### Migration schema errors

**Cause:** django-tenants trying to migrate non-existent tenant schemas.  
**Solution:** This is a known benign error. The migration applies to the public schema successfully. The error occurs for tenant schemas that don't exist in the database yet.

### Overdue task not running

**Cause:** Celery Beat not configured or task not registered.  
**Solution:** Ensure `check_overdue_invoices` is scheduled in `CELERY_BEAT_SCHEDULE` and Celery worker is running.

## Testing

Run invoice tests:

```bash
docker compose exec -T -e DJANGO_SETTINGS_MODULE=config.settings.test_pg backend python -m pytest tests/invoices/ -x -v --tb=short
```
