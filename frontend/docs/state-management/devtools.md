# Zustand DevTools Setup

## Overview

LankaCommerce Cloud POS uses **Redux DevTools Extension** to debug Zustand
stores at runtime. All stores created via `createStore()` automatically
integrate with DevTools in development mode.

---

## 1. Browser Extension Installation

### Chrome

1. Open [Chrome Web Store — Redux DevTools](https://chromewebstore.google.com/detail/redux-devtools/lmhkpmbekcpmknklioeibfkpmmfibljd)
2. Click **Add to Chrome** → **Add Extension**
3. Restart any open `localhost` tabs

### Firefox

1. Open [Firefox Add-ons — Redux DevTools](https://addons.mozilla.org/en-US/firefox/addon/reduxdevtools/)
2. Click **Add to Firefox** → **Add**
3. Restart any open `localhost` tabs

### Edge

1. Open **Edge Add-ons** and search for "Redux DevTools"
2. Click **Get** → **Add Extension**
3. Restart any open `localhost` tabs

---

## 2. Accessing DevTools

1. Open your app at `http://localhost:3000`
2. Open browser DevTools (`F12` or `Ctrl+Shift+I`)
3. Navigate to the **Redux** tab (added by the extension)
4. You should see stores listed under their `LCC/{Domain}` names

---

## 3. Features

| Feature            | Description                                         |
| ------------------ | --------------------------------------------------- |
| **State Inspector** | View current state tree, search properties, raw JSON |
| **Action Log**      | Chronological list of dispatched actions              |
| **Time-Travel**     | Jump to / skip any previous action                   |
| **State Diff**      | Side-by-side comparison of state before/after action  |
| **Export / Import**  | Save and load state snapshots for testing             |

---

## 4. Store Naming Convention

All stores use the `LCC/{Domain}` naming pattern:

| Store        | DevTools Name   |
| ------------ | --------------- |
| UI Store     | `LCC/UI`        |
| Auth Store   | `LCC/Auth`      |
| Theme Store  | `LCC/Theme`     |
| Cart Store   | `LCC/Cart`      |

This naming is configured automatically by the `createStore()` utility via
the `name` parameter.

---

## 5. How It Works

The `createStore()` factory wraps the Zustand initializer with the `devtools`
middleware:

```ts
devtools(innerMiddlewares, {
  name: `LCC/${name}`,
  enabled: process.env.NODE_ENV === 'development',
});
```

- **Enabled only in development** — no overhead in production builds.
- **Middleware order**: DevTools (outer) → Persist → Immer (inner).

---

## 6. Troubleshooting

| Issue                       | Cause                           | Solution                                      |
| --------------------------- | ------------------------------- | --------------------------------------------- |
| Extension not appearing     | Not installed or disabled        | Verify extension is installed and enabled      |
| Store not showing           | DevTools middleware missing      | Use `createStore()` — devtools is on by default |
| Actions not logged          | Incorrect middleware order       | Ensure devtools is the outermost middleware     |
| Performance degrades        | Too much state in DevTools       | Disable for specific stores via `devtools: false` |
| Store shows in production   | `enabled` not environment-gated  | Use default `createStore()` — gated by default  |

---

## 7. Security Notes

- DevTools **expose full store state** in the browser — this is fine for
  development but never ship a production build with DevTools enabled.
- Do **not** share exported state snapshots publicly — they may contain
  user data or tokens.
- The `createStore()` utility disables DevTools in production by default.

---

## 8. Best Practices

1. **Use descriptive action names** — Zustand logs the key names set via
   `set()` or Immer draft mutations.
2. **Keep state flat** — deeply nested state is harder to inspect.
3. **Limit history** — for stores with frequent updates (e.g., timers),
   consider disabling DevTools to avoid memory buildup.
4. **Use time-travel sparingly** — jumping to old states can trigger side
   effects in middleware.
