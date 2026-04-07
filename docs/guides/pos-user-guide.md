# POS User Guide

> **Audience:** Cashiers and store managers.
> This guide covers daily POS operations — from opening a shift to closing
> out at the end of the day.

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Opening a Shift](#opening-a-shift)
4. [Processing a Sale](#processing-a-sale)
5. [Payment Methods](#payment-methods)
6. [Discounts & Promotions](#discounts--promotions)
7. [Holding & Recalling Carts](#holding--recalling-carts)
8. [Voiding a Transaction](#voiding-a-transaction)
9. [Closing a Shift](#closing-a-shift)
10. [Troubleshooting](#troubleshooting)
11. [FAQ](#faq)
12. [Tips & Best Practices](#tips--best-practices)

---

## Overview

The POS system lets you ring up sales, accept payments, and manage your
cash drawer — all from one screen. Every sale you make is tracked under
your **shift** (session), so at the end of the day you can reconcile your
cash and print a summary.

**Roles:**

| Role        | What you can do                                                                                                       |
| ----------- | --------------------------------------------------------------------------------------------------------------------- |
| **Cashier** | Open shift, scan products, process payments, hold/recall carts                                                        |
| **Manager** | Everything a cashier can do, plus: approve large discounts, void transactions, close other users' shifts, run reports |

---

## Getting Started

1. **Log in** with your email and password.
2. You will land on the **POS Dashboard**.
3. **Select your terminal** from the list of available registers.
4. If no terminal is assigned to you, ask your manager.

> **Tip:** If the terminal shows "Inactive" or "Maintenance", a manager
> must activate it before you can start.

---

## Opening a Shift

Before you can make any sales, you need to open a shift.

1. Click **Open Shift** (or the system prompts you automatically).
2. Count the cash in your drawer.
3. Enter the **opening cash amount** (e.g., Rs. 10,000.00).
4. Click **Confirm**.

Your shift is now **open**. You will see your session number at the top
of the screen (e.g., `SESS-POS001-20250615-0001`).

> **Warning:** Only one shift can be open per terminal at a time. If
> another cashier's shift is still open, it must be closed first.

---

## Processing a Sale

### Step 1 — Find the product

You can find products in three ways:

- **Scan the barcode** with the barcode scanner.
- **Type the SKU** or product name into the search bar.
- **Tap a Quick Button** if the product is on your shortcut panel.

### Step 2 — Add to cart

The product appears in your cart. To add more of the same item, scan it
again or tap the **+** button.

### Step 3 — Adjust quantities

- Tap the quantity and type a new number.
- Use **−** to reduce.
- To remove an item completely, swipe left or tap **Remove**.

### Step 4 — Review totals

Check the bottom of the screen:

| Label           | Meaning                |
| --------------- | ---------------------- |
| Subtotal        | Sum of all item prices |
| Discount        | Any discounts applied  |
| Tax             | Calculated tax         |
| **Grand Total** | What the customer pays |

### Step 5 — Accept payment

Tap **Pay** and choose the payment method (see [Payment Methods](#payment-methods)).

### Step 6 — Print receipt

The receipt prints automatically (if enabled). Hand it to the customer.

---

## Payment Methods

### Cash

1. Tap **Cash**.
2. Enter the **amount tendered** (how much the customer gives you).
3. The system shows the **change due**.
4. Give the customer their change and tap **Confirm**.

### Card

1. Tap **Card**.
2. The customer taps or inserts their card.
3. Enter the **authorisation code** from the card terminal.
4. Tap **Confirm**.

> If the card is **declined**, ask the customer for another payment
> method.

### Mobile Payment (FriMi / Genie)

1. Tap **Mobile**.
2. Select **FriMi** or **Genie**.
3. The customer completes the payment on their phone.
4. Enter the **reference number** from the confirmation message.
5. Tap **Confirm**.

### Store Credit

1. Tap **Store Credit**.
2. A customer must be linked to the cart (search by name or phone).
3. Enter the amount to deduct from their credit.

### Split Payment

If the customer wants to pay with multiple methods:

1. Tap **Split Payment**.
2. Enter the amount for the first method (e.g., Rs. 500 cash).
3. Add the second method (e.g., Rs. 300 card).
4. The system shows the remaining balance.
5. Continue until the balance is zero, then confirm.

---

## Discounts & Promotions

### Line Discount (single item)

1. Tap the item in the cart.
2. Tap **Discount**.
3. Choose **Percentage** or **Fixed Amount**.
4. Enter the value (e.g., 10% or Rs. 50).

### Cart Discount (entire sale)

1. Tap **Cart Discount** at the bottom.
2. Choose type and enter value.
3. Optionally enter a **reason** or **coupon code**.

### Manager Approval

Large discounts (above the terminal's `max_discount_percent`) require
manager approval. The manager enters their credentials to authorise.

---

## Holding & Recalling Carts

Sometimes you need to pause a sale — for example, the customer forgot
their wallet.

### Hold a Cart

1. Tap **Hold**.
2. The cart is saved and your screen clears for the next customer.

### Recall a Cart

1. Tap **Held Carts** (or the held-cart icon).
2. Select the cart you want to continue.
3. The items and totals are restored exactly as you left them.
4. Continue with payment.

> You can hold multiple carts at the same time.

---

## Voiding a Transaction

To cancel a sale that has **not yet been completed**:

1. Tap **Void** on the active cart.
2. Enter a **reason** (required for audit).
3. Confirm.

The cart is marked as voided and no payment is charged.

> **Note:** Only managers can void a transaction that has already been
> completed. The manager will need to process a refund.

---

## Closing a Shift

At the end of your shift:

1. Tap **Close Shift**.
2. Count all the cash in your drawer.
3. Enter the **actual cash amount**.
4. The system calculates:
   - **Expected cash** = Opening amount + Cash sales − Cash refunds
   - **Variance** = Actual − Expected
5. Review the shift summary:
   - Total transactions
   - Total sales by payment method
   - Cash variance (over / short)
6. Tap **Confirm Close**.

> **Cash Short:** If you have less cash than expected, the variance will
> be negative. Report this to your manager.
>
> **Cash Over:** If you have more cash than expected, double-check for
> missed refunds or incorrect change.

---

## Troubleshooting

### Product not found when scanning

- Check that the barcode is not damaged or obscured.
- Try typing the barcode number manually.
- Search by product name instead.
- The product may not be marked as "POS Visible" — ask your manager.

### Out of stock

- If the terminal does not allow negative inventory, you cannot sell
  the item.
- Ask your manager to check stock or enable negative inventory.

### Payment declined (card)

- Ask the customer to try another card.
- Offer an alternative payment method (cash, mobile).

### Mobile payment pending

- Wait for the customer to complete the payment on their phone.
- Verify the reference number matches the confirmation message.

### Receipt not printing

- Check that the printer is turned on and connected.
- Verify the printer IP address in terminal settings.
- Try printing a test receipt from the terminal settings screen.

### Session won't close

- Make sure all active carts are completed or voided.
- If a cart is held, recall and complete it, or void it.

---

## FAQ

**Q: Can I sell without opening a shift?**
A: No. You must open a shift first. This ensures all sales are tracked
and cash can be reconciled.

**Q: Can I open a shift on someone else's terminal?**
A: Only if that terminal does not already have an open shift. Each
terminal allows one open shift at a time.

**Q: How do I handle a return?**
A: Returns are processed as refunds by a manager. Go to the payment
history, find the original transaction, and tap **Refund**.

**Q: What happens if the internet goes down?**
A: If offline mode is enabled on your terminal, you can continue
processing sales. They will sync when connectivity is restored.

**Q: Can I change the price of an item?**
A: Only if "Allow Price Override" is enabled on your terminal. Tap the
item, then tap **Edit Price**.

**Q: How do I apply a coupon code?**
A: Use the Cart Discount feature and enter the coupon code in the
coupon field.

---

## Tips & Best Practices

1. **Count your cash carefully** when opening and closing your shift.
   Accurate counts prevent unexplained variances.

2. **Scan barcodes** whenever possible — it is faster and more accurate
   than searching by name.

3. **Hold carts** instead of voiding them if the customer will come back.
   Held carts preserve all items and discounts.

4. **Always enter a reason** when voiding. This helps managers review
   voids during audit.

5. **Check the grand total** before accepting payment. Confirm it matches
   what the customer expects.

6. **Print a shift summary** when closing. Keep a copy for your records.

7. **Lock your screen** when stepping away from the terminal.

8. **Report issues immediately** — low receipt paper, scanner problems,
   or cash discrepancies. Early reporting prevents bigger problems.
