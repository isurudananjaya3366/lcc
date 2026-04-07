# POS Offline Operations Guide

> **Audience:** POS operators, store managers, and support staff  
> **Purpose:** How to use the POS terminal when the internet is unavailable

---

## What Is Offline Mode?

Offline mode lets you continue making sales, creating customers, and viewing product information even when the internet connection is lost. All your work is saved on the device and automatically sent to the server when the connection returns.

---

## How to Tell You're Offline

When the internet drops, you'll see:

- **Red "Offline" indicator** in the header bar
- **Yellow banner** at the top of the screen: "You are currently offline"
- **Pending count badge** showing queued transactions

```
┌─────────────────────────────────────────┐
│  🔴 OFFLINE MODE                    ⚙️  │
│  Last synced: 5 minutes ago             │
│  Pending transactions: 3                │
└─────────────────────────────────────────┘
```

---

## What You Can Do Offline

| Operation            | Available? | Notes                       |
| -------------------- | ---------- | --------------------------- |
| Search products      | ✅ Yes     | From cached data            |
| View product details | ✅ Yes     | If product is cached        |
| Add to cart          | ✅ Yes     | Always works                |
| Complete sale        | ✅ Yes     | Queued for sync             |
| Create customer      | ✅ Yes     | Queued for sync             |
| View customer        | ✅ Yes     | If customer is cached       |
| Cash payment         | ✅ Yes     | Recommended offline         |
| Card payment         | ⚠️ Queued  | May fail if gateway offline |
| Generate reports     | ❌ No      | Requires server             |
| Change prices        | ❌ No      | Requires server             |
| Update inventory     | ⚠️ Limited | Local adjustments only      |

---

## Making a Sale Offline

1. **Search for products** using the search bar (from cached data).
2. **Add items** to the cart as usual.
3. **Select payment method** — cash is recommended while offline.
4. **Complete the sale** — the transaction is saved locally.
5. You'll see a confirmation: "Sale queued — will sync when online."
6. The pending transaction count increases by 1.

---

## Creating a Customer Offline

1. Open the **Customer** section.
2. Fill in the customer details (name, phone, email).
3. **Save** — the customer receives a temporary offline ID.
4. The customer is available immediately for use in sales.
5. When online, the customer syncs and receives a permanent ID.

---

## Understanding Sync Status

When your connection returns, syncing happens automatically:

```
┌─────────────────────────────────────────┐
│  Syncing...                             │
│  ████████░░░░░░░░░░░░░░░░░░░  3/10     │
│  Uploading transaction 3 of 10          │
└─────────────────────────────────────────┘
```

### Status indicators

| Indicator              | Meaning                      |
| ---------------------- | ---------------------------- |
| 🟢 Green dot (pulsing) | Online, connected            |
| 🔴 Red dot             | Offline                      |
| 🔵 Blue spinner        | Syncing in progress          |
| ⚠️ Yellow warning      | Sync completed with warnings |

After sync completes, you'll see a notification confirming how many transactions were sent.

---

## Handling Sync Conflicts

Sometimes the same record is changed both offline and on the server. When this happens:

1. A **conflict dialog** appears showing both versions side by side.
2. **Your version** is shown on the left (blue).
3. **Server version** is shown on the right (green).
4. Choose which version to keep, or select "Merge."
5. Click **Apply** to confirm.

```
┌─────────────────────────────────────────┐
│  ⚠️ Conflict Detected                   │
│                                         │
│  Product: ABC123 - Office Chair         │
│                                         │
│  Your version:    Rs. 15,000            │
│  Server version:  Rs. 14,500            │
│                                         │
│  ⚪ Use your version                    │
│  ⚪ Use server version                  │
│  ⚪ Merge both changes                  │
│                                         │
│  [ Cancel ]  [ Apply ]                  │
└─────────────────────────────────────────┘
```

---

## Emergency Backup

If you're worried about losing data:

1. Go to **Settings > Offline**.
2. Click **Sync > Export** from the menu.
3. A JSON file downloads with all your queued transactions.
4. Keep this file safe — it can be imported on another device.

To import: go to **Settings > Offline** and use the import option.

---

## Best Practices

1. **Sync regularly** — Don't let pending transactions pile up.
2. **Monitor the pending count** — Check it periodically.
3. **Use cash offline** — Card payments may not process without internet.
4. **Export before browser updates** — Save your data before clearing browser data.
5. **Report persistent failures** — If sync keeps failing, contact support.

---

## Troubleshooting

| Problem                       | What to Do                                               |
| ----------------------------- | -------------------------------------------------------- |
| Offline mode won't turn off   | Check internet connection; try refreshing the browser    |
| Transactions not syncing      | Wait 5 minutes for auto-retry; try manual sync           |
| Product not showing in search | Refresh cache from Settings > Offline                    |
| Sync fails repeatedly         | Check the error in Sync History; contact support         |
| Data seems missing            | Check Sync History for errors; verify on the back office |

### When to Contact Support

- Sync fails more than 5 times for the same transaction
- Conflict dialog shows unexpected data
- Pending count keeps increasing even when online
- You see error codes you don't understand

Provide the **error message** and **sync history export** when contacting support.
