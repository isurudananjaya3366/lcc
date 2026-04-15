# POS Testing Checklist

## Product Search (Tasks 33-38)

| #   | Scenario             | Steps                        | Expected Result                     | Status |
| --- | -------------------- | ---------------------------- | ----------------------------------- | ------ |
| 1   | Text search          | Type "rice" in search        | Products containing "rice" appear   | ☐      |
| 2   | Barcode scan         | Scan valid barcode           | Product found and added to cart     | ☐      |
| 3   | Invalid barcode      | Scan >13 char barcode        | Rejected (no API call)              | ☐      |
| 4   | Empty search         | Clear search field           | Results hidden, quick buttons shown | ☐      |
| 5   | Quick button add     | Click quick button           | Product added to cart immediately   | ☐      |
| 6   | Quick button variant | Click button with variants   | Variant selection modal opens       | ☐      |
| 7   | Search result limit  | Search term with 50+ results | Max 10 visible, "Showing X of Y"    | ☐      |
| 8   | Keyboard navigation  | Arrow keys in results        | Highlight moves up/down             | ☐      |
| 9   | Enter to select      | Press Enter on highlighted   | Product added to cart               | ☐      |
| 10  | Escape to clear      | Press Escape during search   | Search field cleared                | ☐      |

## Cart Management (Tasks 39-52)

| #   | Scenario            | Steps                          | Expected Result                   | Status |
| --- | ------------------- | ------------------------------ | --------------------------------- | ------ |
| 11  | Add item            | Select product from search     | Item appears in cart with qty 1   | ☐      |
| 12  | Increase quantity   | Click + on cart item           | Quantity increments by 1          | ☐      |
| 13  | Decrease quantity   | Click - on cart item (qty > 1) | Quantity decrements by 1          | ☐      |
| 14  | Remove at zero      | Click - on cart item (qty = 1) | Item removed from cart            | ☐      |
| 15  | Direct quantity     | Click qty, type new number     | Quantity updates to entered value | ☐      |
| 16  | Remove item         | Click trash icon               | Item removed from cart            | ☐      |
| 17  | Item discount %     | Apply 10% discount to item     | Line total reduced by 10%         | ☐      |
| 18  | Item discount fixed | Apply ₨100 fixed discount      | Line total reduced by ₨100        | ☐      |
| 19  | Clear cart          | Click clear, confirm           | All items removed                 | ☐      |
| 20  | Long item name      | Add item with very long name   | Name truncated with tooltip       | ☐      |

## Totals & Discounts (Tasks 53-66)

| #   | Scenario                | Steps                          | Expected Result                                | Status |
| --- | ----------------------- | ------------------------------ | ---------------------------------------------- | ------ |
| 21  | Subtotal                | Add multiple items             | Subtotal = sum of line totals                  | ☐      |
| 22  | Cart discount %         | Apply 15% cart discount        | Discount amount = 15% of subtotal              | ☐      |
| 23  | Cart discount fixed     | Apply ₨500 fixed discount      | Discount = ₨500 or subtotal (whichever less)   | ☐      |
| 24  | Discount preview        | Open discount modal with value | Live preview shows subtotal → discount → total | ☐      |
| 25  | Tax calculation         | Check tax display              | 15% VAT on (subtotal - discount)               | ☐      |
| 26  | Grand total             | Verify grand total             | Subtotal - discount + tax                      | ☐      |
| 27  | Items count             | Add 5 items                    | Count shows "5 items"                          | ☐      |
| 28  | Edit discount           | Click Edit on applied discount | Modal opens with current values                | ☐      |
| 29  | Remove discount         | Click Remove on discount       | Discount cleared                               | ☐      |
| 30  | Discount reason "Other" | Select "Other" reason          | Free-text input appears                        | ☐      |

## Payment Processing (Tasks 67-82)

| #   | Scenario        | Steps                       | Expected Result                     | Status |
| --- | --------------- | --------------------------- | ----------------------------------- | ------ |
| 31  | Cash exact      | Enter exact amount          | Change = ₨0.00                      | ☐      |
| 32  | Cash overpay    | Enter more than due         | Change amount shown in green        | ☐      |
| 33  | Cash underpay   | Enter less than due         | Remaining shown in amber            | ☐      |
| 34  | Quick amount    | Click "Round to ₨1000"      | Amount set to rounded value         | ☐      |
| 35  | Card payment    | Select card, fill details   | Complete button enabled             | ☐      |
| 36  | Card validation | Enter 3-digit last digits   | Validation error shown              | ☐      |
| 37  | Bank transfer   | Enter reference             | Complete button enabled             | ☐      |
| 38  | Split payment   | Toggle split, add 2 methods | Both payments listed, total correct | ☐      |
| 39  | Customer attach | Search and select customer  | Customer name shown in payment      | ☐      |
| 40  | Complete sale   | Click Complete Sale         | Receipt modal opens                 | ☐      |

## Receipt (Tasks 83-87)

| #   | Scenario         | Steps                       | Expected Result                            | Status |
| --- | ---------------- | --------------------------- | ------------------------------------------ | ------ |
| 41  | Receipt display  | Complete a sale             | Receipt modal shows with formatted content | ☐      |
| 42  | Print receipt    | Click Print or press P      | Browser print dialog opens                 | ☐      |
| 43  | Email receipt    | Click Email, enter address  | Email dialog opens, validates, sends       | ☐      |
| 44  | Email validation | Enter invalid email         | Error message shown                        | ☐      |
| 45  | New sale         | Click New Sale or press N   | Cart cleared, receipt closed               | ☐      |
| 46  | Auto-focus       | Wait 2s after receipt opens | New Sale button auto-focused               | ☐      |

## Shift Management (Tasks 87-94)

| #   | Scenario            | Steps                         | Expected Result                          | Status |
| --- | ------------------- | ----------------------------- | ---------------------------------------- | ------ |
| 47  | Shift open          | Enter cash, click Open        | POS becomes operational                  | ☐      |
| 48  | Quick amounts       | Click 10K button              | Value set to 10,000                      | ☐      |
| 49  | Shift close summary | Open close modal              | Shows transactions, sales, expected      | ☐      |
| 50  | Cash count          | Enter denomination quantities | Running total updates                    | ☐      |
| 51  | Cash count keyboard | Tab/Enter between fields      | Focus moves to next denomination         | ☐      |
| 52  | Clear all counts    | Click Clear All               | All counts reset to 0                    | ☐      |
| 53  | Variance balanced   | Count matches expected        | Green "Perfect Match" shown              | ☐      |
| 54  | Variance minor      | Count off by ₨5               | Green "Acceptable" shown                 | ☐      |
| 55  | Variance major      | Count off by ₨600             | Red "Major Discrepancy" + manager review | ☐      |
| 56  | Close shift         | Click Close Shift             | Session closed, shift cleared            | ☐      |

## Hold & Retrieve (Tasks 95-96)

| #   | Scenario         | Steps                       | Expected Result              | Status |
| --- | ---------------- | --------------------------- | ---------------------------- | ------ |
| 57  | Hold sale        | Click Hold, enter reason    | Cart saved and cleared       | ☐      |
| 58  | Hold limit       | Try to hold 11th sale       | Error: max 10 holds          | ☐      |
| 59  | Retrieve sale    | Click Retrieve, select hold | Cart restored from held data | ☐      |
| 60  | Hold badge count | Hold 3 sales                | Badge shows "3"              | ☐      |

## Keyboard Shortcuts

| #   | Shortcut    | Expected Action          | Status |
| --- | ----------- | ------------------------ | ------ |
| 61  | F2          | Focus product search     | ☐      |
| 62  | F3          | Open payment modal       | ☐      |
| 63  | F4          | Hold sale dialog         | ☐      |
| 64  | F5          | Retrieve held sale       | ☐      |
| 65  | Escape      | Close active modal       | ☐      |
| 66  | P (receipt) | Print receipt            | ☐      |
| 67  | E (receipt) | Email receipt            | ☐      |
| 68  | N (receipt) | New sale                 | ☐      |
| 69  | Delete      | Remove focused cart item | ☐      |

## Performance Benchmarks

| Metric                 | Target | Acceptable | Status |
| ---------------------- | ------ | ---------- | ------ |
| Barcode scan to result | <50ms  | <100ms     | ☐      |
| Search results appear  | <200ms | <500ms     | ☐      |
| Add to cart response   | <100ms | <200ms     | ☐      |
| Modal open/close       | <200ms | <300ms     | ☐      |
| Payment completion     | <1s    | <3s        | ☐      |
