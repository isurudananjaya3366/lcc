# Quote Module Configuration

## QuoteSettings (Per-Tenant)

Each tenant can configure their quote defaults via the `QuoteSettings` model:

| Setting                 | Default | Description                     |
| ----------------------- | ------- | ------------------------------- |
| `default_currency`      | `LKR`   | Default currency for new quotes |
| `default_validity_days` | `30`    | Days until quote expires        |
| `auto_numbering`        | `True`  | Auto-generate quote numbers     |
| `number_prefix`         | `QT`    | Prefix for quote numbers        |
| `require_customer`      | `False` | Require customer on quotes      |
| `allow_zero_price`      | `False` | Allow zero-price line items     |

## Celery Tasks

### Periodic Tasks (Celery Beat)

| Task                         | Schedule | Description                                           |
| ---------------------------- | -------- | ----------------------------------------------------- |
| `send_expiry_reminders_task` | Daily    | Find quotes expiring within 3 days and send reminders |
| `bulk_expire_quotes`         | Daily    | Auto-expire past-due sent quotes                      |

### Async Tasks

| Task                        | Retry                                     | Description          |
| --------------------------- | ----------------------------------------- | -------------------- |
| `send_quote_email_task`     | 3 retries, exponential backoff (max 600s) | Send quote email     |
| `send_expiry_reminder_task` | 3 retries, exponential backoff (max 600s) | Send expiry reminder |

## Signals

| Signal                       | Trigger              | Effect                                    |
| ---------------------------- | -------------------- | ----------------------------------------- |
| `recalculate_on_line_save`   | LineItem post_save   | Recalculate quote totals + regenerate PDF |
| `recalculate_on_line_delete` | LineItem post_delete | Recalculate quote totals + regenerate PDF |
| `capture_quote_pre_save`     | Quote pre_save       | Capture old values for history            |
| `log_quote_post_save`        | Quote post_save      | Log changes to QuoteHistory               |

## Email Templates

Required templates in `templates/quotes/emails/`:

- `quote_email.html` / `quote_email.txt` — Main quote email
- `expiry_reminder.html` / `expiry_reminder.txt` — Expiry warning email

## Dependencies

- `reportlab>=4.0` — PDF generation
- `celery` — Async task processing
- `django-filter` — API filtering
- `django-tenants` — Multi-tenancy support
