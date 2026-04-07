# POS Troubleshooting

## Common Issues

### "Terminal is not active"

**Cause:** Attempting to open a session on an `inactive` or `maintenance`
terminal.

**Fix:** Activate the terminal first:

```http
POST /api/v1/pos/terminals/{id}/activate/
```

---

### "Cannot deactivate — terminal has an open session" (409)

**Cause:** Trying to deactivate or put a terminal into maintenance while
a session is still open.

**Fix:** Close the session first:

```http
POST /api/v1/pos/sessions/{id}/close_session/
{"actual_cash_amount": "..."}
```

---

### "Session is not open"

**Cause:** Attempting an operation (payment, cart modification) on a
session that is already closed, suspended, or force-closed.

**Fix:** Open a new session, or resume a suspended session.

---

### "Active cart not found" (404 on payment)

**Cause:** The cart UUID is wrong, or the cart status is no longer `active`
(e.g., already completed or voided).

**Fix:** Check the cart UUID and its current status.

---

### "Cart is not fully paid"

**Cause:** Calling `complete_transaction()` or the `/payment/complete/`
endpoint before the remaining amount reaches zero.

**Fix:** Process additional payments until `get_remaining_amount() == 0`.

---

### "Store credit requires a customer"

**Cause:** `process_store_credit()` called on a cart without a linked
customer.

**Fix:** Assign a customer to the cart before processing store credit.

---

### Cash variance after closing session

**Cause:** The actual cash counted does not match the expected cash
(`opening + sales − refunds`).

**Investigation:**

1. Check `session.total_sales` and `session.total_refunds` against the
   payment records.
2. Verify that all card/mobile payments were recorded correctly (they
   should not affect the expected cash figure unless the POS counts
   them separately).
3. Look for voided transactions that may have already dispensed cash.

---

## Error Codes

| HTTP Status | When                                                                   |
| ----------- | ---------------------------------------------------------------------- |
| 400         | Validation failure, bad request body, business rule violation          |
| 401         | Missing or invalid JWT / session authentication                        |
| 404         | Resource not found (terminal, session, cart, payment, product)         |
| 409         | Conflict (deactivate with open session, maintenance with open session) |

---

## Debugging Tips

### Enable Debug Logging

```python
LOGGING = {
    "loggers": {
        "apps.pos": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
    },
}
```

POS views log key events: session open/close, item added, payment processed.

### Inspect Cart State

```python
from apps.pos.cart.models import POSCart

cart = POSCart.objects.get(pk="<uuid>")
print(cart.status, cart.grand_total, cart.items.count())
for item in cart.items.filter(is_active=True, is_deleted=False):
    print(item.product.name, item.quantity, item.line_total)
```

### Check Payment Balance

```python
from apps.pos.payment.services.payment_service import PaymentService

svc = PaymentService(cart=cart, user=user)
print("Remaining:", svc.get_remaining_amount())
print("Can complete:", svc.can_complete_cart())
```

### Session Counters Mismatch

If `session.transaction_count` or `session.total_sales` look wrong:

```python
from apps.pos.cart.models import POSCart
from apps.pos.constants import CART_STATUS_COMPLETED

actual = POSCart.objects.filter(
    session=session, status=CART_STATUS_COMPLETED
).count()
print(f"Model: {session.transaction_count}, Actual: {actual}")
```

---

## Performance

- **Product search** uses `select_related()` to minimise queries.
- **Cart views** use `prefetch_related("items__product", "items__variant")`.
- **Session counters** use `F()` expressions — no extra SELECT before UPDATE.
- For high-volume terminals, consider indexing `POSCart.session` +
  `POSCart.status` as a composite index.
