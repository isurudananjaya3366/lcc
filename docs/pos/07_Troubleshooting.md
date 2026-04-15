# POS Troubleshooting

## Common Issues

### POS Page Shows Blank Screen

**Cause:** JavaScript error in console.
**Fix:** Check browser console for errors. Most common: missing environment variables or API connection failure.

### "No Active Shift" Modal Won't Close

**Cause:** This is by design. A shift must be opened before using the POS.
**Fix:** Enter opening cash amount and click "Open Shift".

### Products Not Appearing in Search

**Cause:** Backend API not responding or no products in database.
**Fix:**

1. Check backend is running: `docker compose ps`
2. Verify products exist: `docker compose exec backend python manage.py shell -c "from apps.pos.models import Product; print(Product.objects.count())"`
3. Check network tab for API errors

### Cart Not Persisting After Refresh

**Cause:** localStorage may be cleared or full.
**Fix:** Check localStorage for key `lcc-pos-cart`. Clear browser data and try again.

### Payment Fails with Error

**Cause:** Backend validation failure.
**Fix:**

1. Check that cart has items
2. Verify payment amount covers grand total
3. Check error message for specific validation issue
4. Ensure active shift exists

### Receipt Not Printing

**Cause:** Browser print dialog blocked or printer not configured.
**Fix:** Check popup blocker settings. Ensure printer is connected and set as default.

### Email Receipt Fails

**Cause:** Backend email service not configured.
**Fix:** Verify SMTP settings in backend configuration. Check backend logs for email errors.

### Barcode Scanner Not Working

**Cause:** Scanner not in keyboard emulation mode.
**Fix:**

1. Ensure scanner is in HID (keyboard) mode
2. Click search field to focus it
3. Scan barcode — characters should appear in search
4. Scanner must send Enter key after barcode

### Shift Variance Shows Wrong Expected Cash

**Cause:** Expected cash calculated from opening cash + cash sales only.
**Fix:** Verify opening cash was entered correctly. Cash refunds and withdrawals affect the expected amount.

### Hold Sale Limit Reached

**Cause:** Maximum 10 held sales per session.
**Fix:** Retrieve and complete some held sales before holding more.

## Error Messages

| Error                     | Meaning                           | Action                        |
| ------------------------- | --------------------------------- | ----------------------------- |
| "Failed to open shift"    | API call to create session failed | Check backend connectivity    |
| "Failed to close shift"   | Session close API error           | Retry; check backend logs     |
| "Failed to complete sale" | Payment processing error          | Verify payment details; retry |
| "Failed to send email"    | Email service error               | Check SMTP config; retry      |

## Support

For development issues, check:

1. Browser console for frontend errors
2. Docker logs: `docker compose logs backend`
3. Network tab for API request/response details
