# Responsive Design & Breakpoints

LankaCommerce Cloud uses a mobile-first responsive design system built on Tailwind CSS breakpoints with custom utility classes for common layout patterns.

---

## Breakpoints

| Token | Width   | Typical Use               |
| ----- | ------- | ------------------------- |
| `xs`  | 475px   | Large phones              |
| `sm`  | 640px   | Small tablets, landscape  |
| `md`  | 768px   | Tablets                   |
| `lg`  | 1024px  | Small desktops            |
| `xl`  | 1280px  | Desktops                  |
| `2xl` | 1536px  | Large desktops            |
| `3xl` | 1920px  | Ultra-wide / 4K           |

### Mobile-First Approach

Tailwind applies styles from smallest up. Unprefixed utilities apply to all sizes; prefixed utilities (`md:`, `lg:`, etc.) apply at that breakpoint and above.

```tsx
<p className="text-sm md:text-base lg:text-lg">Responsive text</p>
```

---

## Responsive Typography

Pre-built component classes for common heading/body patterns:

| Class                   | Mobile     | md          | lg          | xl          |
| ----------------------- | ---------- | ----------- | ----------- | ----------- |
| `.responsive-heading-xl` | `text-3xl` | `text-4xl`  | `text-5xl`  | `text-6xl`  |
| `.responsive-heading-lg` | `text-2xl` | `text-3xl`  | `text-4xl`  | —           |
| `.responsive-heading-md` | `text-xl`  | `text-2xl`  | `text-3xl`  | —           |
| `.responsive-heading-sm` | `text-lg`  | `text-xl`   | `text-2xl`  | —           |
| `.responsive-body-lg`    | `text-base`| `text-lg`   | —           | —           |
| `.responsive-body`       | `text-sm`  | `text-base` | —           | —           |
| `.responsive-body-sm`    | `text-xs`  | `text-sm`   | —           | —           |

```tsx
<h1 className="responsive-heading-xl">Dashboard</h1>
<p className="responsive-body">Welcome back</p>
```

---

## Responsive Spacing

Section spacing utilities scale across breakpoints:

| Class                | Mobile    | md        | lg        |
| -------------------- | --------- | --------- | --------- |
| `.section-spacing`   | `py-12`   | `py-16`   | `py-20`   |
| `.section-spacing-sm`| `py-8`    | `py-10`   | `py-12`   |
| `.section-spacing-lg`| `py-16`   | `py-20`   | `py-24`   |

---

## Responsive Grid Patterns

### Dashboard Cards

```tsx
<div className="grid-dashboard-cards">
  {/* Auto-fit, min 280px per card */}
</div>
```

### Form Grids

```tsx
<div className="grid-form-2col"> {/* 2 cols → 1 col below sm */}
<div className="grid-form-3col"> {/* 3 cols → 1 col below md */}
```

### Stats Grid

```tsx
<div className="grid-stats"> {/* 4 cols → 2 cols (md) → 1 col (sm) */}
```

---

## Sidebar Responsive Behavior

The sidebar uses CSS classes for three states:

| State      | Width  | Trigger              |
| ---------- | ------ | -------------------- |
| Expanded   | 240px  | Default on `lg+`     |
| Collapsed  | 64px   | `.sidebar-collapsed` |
| Mobile     | 280px  | Fixed drawer on `<md`|

### Classes

- `.sidebar` — Base sidebar (240px, full height, border-right)
- `.sidebar-collapsed` — Narrow mode (64px)
- `.sidebar.open` — Visible on mobile (slides in from left)
- `.sidebar-overlay` — Backdrop for mobile drawer (add `.active` to show)
- `.main-content` — Adjusts margin with sidebar transitions

### Mobile Sidebar Pattern

```tsx
<div className={`sidebar ${isOpen ? 'open' : ''}`}>
  {/* Sidebar content */}
</div>
<div className={`sidebar-overlay ${isOpen ? 'active' : ''}`}
     onClick={() => setIsOpen(false)} />
<main className="main-content">
  {/* Page content */}
</main>
```

---

## Table Responsive Patterns

### Horizontal Scroll

```tsx
<div className="table-responsive">
  <table>{/* Wide table scrolls horizontally */}</table>
</div>
```

### Scroll Shadow Indicator

```tsx
<div className="table-responsive table-responsive-shadow">
  <table>{/* Fade on right edge hints at scrollable content */}</table>
</div>
```

### Column Priority System

Hide less-important columns on smaller screens:

| Class            | Hidden below |
| ---------------- | ------------ |
| `.col-priority-3`| `sm` (640px) |
| `.col-priority-4`| `md` (768px) |

```tsx
<th className="col-priority-4">Notes</th>  {/* Hidden on phone + tablet */}
<th className="col-priority-3">Status</th> {/* Hidden on phone only */}
```

### Card View for Mobile

Transform a table into stacked cards for mobile:

```tsx
<table className="table-card-view">
  <thead>...</thead>
  <tbody>
    <tr>
      <td data-label="Name">Product A</td>
      <td data-label="Price">$10.00</td>
    </tr>
  </tbody>
</table>
```

Each `<td>` uses `data-label` to render a label prefix when stacked.

---

## Print Styles

### Utility Classes

| Class                    | Purpose                              |
| ------------------------ | ------------------------------------ |
| `.no-print`              | Hidden when printing                 |
| `.print-only`            | Visible only when printing           |
| `.print-visible`         | Mark buttons to keep during print    |
| `.print-page-break`      | Force page break before element      |
| `.print-page-break-after`| Force page break after element       |
| `.print-no-break`        | Prevent page break inside element    |
| `.print-invoice`         | Full-width invoice layout            |
| `.print-receipt`         | 80mm receipt layout, centered        |
| `.print-report`          | Full-width report layout             |

### Auto-Hidden Elements

Navigation, sidebar, footer, buttons, and scrollbar-hide elements are automatically hidden during print.

### Usage

```tsx
<button className="no-print" onClick={window.print}>Print</button>

<div className="print-only">
  <p>This appears only on the printed page.</p>
</div>

<div className="print-invoice">
  <div className="print-no-break">
    {/* Invoice header — won't split across pages */}
  </div>
  <table>{/* Line items */}</table>
  <div className="print-page-break" />
  {/* Second page content */}
</div>
```

---

## Container

The container is centered with responsive padding:

| Breakpoint | Padding |
| ---------- | ------- |
| Default    | 1rem    |
| `md`       | 1.5rem  |
| `lg+`      | 2rem    |

```tsx
<div className="container">{/* Centered, responsive padding */}</div>
```

---

## Best Practices

1. **Mobile-first**: Write base styles for mobile, add breakpoint prefixes for larger screens
2. **Use responsive utilities**: Prefer `.responsive-heading-*` over manual breakpoint classes
3. **Test all breakpoints**: Verify layouts at `xs`, `sm`, `md`, `lg`, `xl`, and `2xl`
4. **Sidebar awareness**: Always wrap page content in `.main-content` for sidebar transition support
5. **Print testing**: Use browser print preview to verify `.no-print` / `.print-only` behavior
6. **Column priority**: Assign `.col-priority-3` or `.col-priority-4` to less critical table columns
7. **Card view data-label**: Always add `data-label` attributes when using `.table-card-view`
