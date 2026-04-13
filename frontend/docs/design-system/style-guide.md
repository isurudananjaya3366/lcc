# LankaCommerce Cloud — Design System Style Guide

Complete reference for the Tailwind CSS design system used across the LankaCommerce Cloud frontend.

---

## Overview

The design system is built on Tailwind CSS 3.x with custom theme extensions, CSS custom properties (HSL color tokens), and layered utility classes. It provides:

- **Color System** — HSL-based palettes with semantic color mapping
- **Typography** — Inter font family with responsive type scale
- **Spacing & Layout** — 4px base unit, responsive grids, section spacing
- **Responsive Design** — Mobile-first with 7 breakpoints (xs → 3xl)
- **Animations** — Transition scales, keyframe animations, reduced motion support
- **Accessibility** — Focus rings, disabled states, WCAG 2.1 compliance
- **Print Styles** — Invoice, receipt, and report formatting

---

## File Structure

```
frontend/
├── tailwind.config.ts          # Theme configuration (breakpoints, colors, fonts, animations)
├── postcss.config.mjs          # PostCSS with Tailwind + Autoprefixer
├── styles/
│   ├── variables.css           # CSS custom properties (design tokens)
│   └── animations.css          # Keyframe definitions & animation utilities
├── app/
│   ├── globals.css             # Base/component/utility layers + print styles
│   └── layout.tsx              # Font loading (Inter via next/font)
└── docs/
    └── design-system/
        ├── colors.md           # Color system documentation
        ├── typography.md       # Typography system documentation
        ├── spacing.md          # Spacing & layout documentation
        ├── responsive.md       # Responsive design documentation
        ├── animations.md       # Animation system documentation
        └── style-guide.md      # This file
```

---

## Colors

### Palettes

Six HSL color palettes with 50–950 shades defined as CSS custom properties:

| Palette     | Hue   | Usage                        |
| ----------- | ----- | ---------------------------- |
| `primary`   | Blue  | Brand, CTA, links            |
| `secondary` | Slate | Text, backgrounds, borders   |
| `success`   | Green | Positive states, completed   |
| `warning`   | Amber | Caution, pending states      |
| `error`     | Red   | Errors, destructive actions  |
| `info`      | Cyan  | Informational, processing    |

### Semantic Colors

| Token          | Light                  | Dark                   |
| -------------- | ---------------------- | ---------------------- |
| `background`   | White                  | Slate 950              |
| `foreground`   | Slate 950              | Slate 50               |
| `card`         | White                  | Slate 900              |
| `muted`        | Slate 100              | Slate 800              |
| `accent`       | Slate 100              | Slate 800              |
| `border`       | Slate 200              | Slate 800              |

### Usage

```tsx
<div className="bg-background text-foreground" />
<div className="bg-primary-500 text-primary-foreground" />
<span className="text-success-600" />
```

See [colors.md](colors.md) for full reference.

---

## Typography

### Font Family

- **Sans**: Inter → system fallback stack (includes Noto Sans for Sinhala/Tamil)
- **Mono**: SF Mono → Consolas → Monaco → system monospace
- **Display**: Alias for sans (future custom display font)

### Type Scale

| Class       | Size     | Line Height |
| ----------- | -------- | ----------- |
| `text-xs`   | 0.75rem  | 1rem        |
| `text-sm`   | 0.875rem | 1.25rem     |
| `text-base` | 1rem     | 1.5rem      |
| `text-lg`   | 1.125rem | 1.75rem     |
| `text-xl`   | 1.25rem  | 1.75rem     |
| `text-2xl`  | 1.5rem   | 2rem        |
| `text-3xl`  | 1.875rem | 2.25rem     |
| `text-4xl`  | 2.25rem  | 2.5rem      |
| `text-5xl`  | 3rem     | 1           |
| `text-6xl`  | 3.75rem  | 1           |

### Responsive Typography

```tsx
<h1 className="responsive-heading-xl">Page Title</h1>
<p className="responsive-body">Body text</p>
```

See [typography.md](typography.md) for full reference.

---

## Spacing

### Base Unit: 4px

Extended spacing values: `0.5` (2px), `1.5` (6px), `2.5` (10px), `3.5` (14px), `18` (72px), `22` (88px), `26` (104px), `30` (120px).

### Container

Centered with responsive padding (1rem → 1.5rem → 2rem).

### Grid Utilities

| Class                   | Behavior                              |
| ----------------------- | ------------------------------------- |
| `.grid-dashboard-cards` | Auto-fit, min 280px                   |
| `.grid-form-2col`       | 2 cols → 1 col below sm              |
| `.grid-form-3col`       | 3 cols → 1 col below md              |
| `.grid-stats`           | 4 → 2 → 1 cols                       |

See [spacing.md](spacing.md) for full reference.

---

## Responsive Design

### Breakpoints

| Token | Width  |
| ----- | ------ |
| `xs`  | 475px  |
| `sm`  | 640px  |
| `md`  | 768px  |
| `lg`  | 1024px |
| `xl`  | 1280px |
| `2xl` | 1536px |
| `3xl` | 1920px |

### Key Patterns

- **Sidebar**: Expanded (240px) → collapsed (64px) → mobile drawer (280px)
- **Tables**: Horizontal scroll + column priorities + card view for mobile
- **Print**: Full set of print utilities (`.no-print`, `.print-only`, page breaks)

See [responsive.md](responsive.md) for full reference.

---

## Animations

### Transition Scale

`duration-75` through `duration-500` with `ease-in`, `ease-out`, `ease-in-out`.

### Animation Classes

| Class                   | Effect          |
| ----------------------- | --------------- |
| `animate-fade-in`       | Fade in         |
| `animate-slide-in-up`   | Slide up        |
| `animate-slide-in-down` | Slide down      |
| `animate-scale-in`      | Scale zoom      |
| `animate-spin`          | Loading spinner |
| `animate-pulse`         | Skeleton loader |
| `animate-shake`         | Error feedback  |

All animations respect `prefers-reduced-motion`.

See [animations.md](animations.md) for full reference.

---

## Accessibility

### Focus Rings

Global `:focus-visible` applies a 2px primary-colored outline with offset. Component classes:

```tsx
<button className="focus-ring">Explicit focus ring</button>
<input className="focus-ring-inset" />
```

### Disabled States

```tsx
<button className="disabled">Not available</button>
{/* Or use Tailwind: */}
<button className="disabled:opacity-50 disabled:cursor-not-allowed" disabled>
  Not available
</button>
```

### Selection Colors

Text selection uses primary palette colors, with dark mode support.

### Reduced Motion

All animations auto-disable when user has `prefers-reduced-motion: reduce` enabled.

---

## Scrollbar

Custom scrollbar styling applied globally:

- **Width**: 8px (both axes)
- **Thumb**: Muted color, 4px border-radius
- **Hover**: Slightly darker thumb
- **Firefox**: Uses `scrollbar-width: thin`

Use `.scrollbar-hide` to completely hide scrollbars while preserving scroll.

---

## Dark Mode

Dark mode is class-based (`darkMode: 'class'`). Toggle by adding/removing `.dark` on `<html>`.

All design tokens have dark mode overrides in `variables.css`. Semantic color utilities (`bg-background`, `text-foreground`, etc.) automatically adapt.

---

## Plugins

| Plugin                    | Purpose                          |
| ------------------------- | -------------------------------- |
| `@tailwindcss/typography` | Prose formatting for rich text   |
| `@tailwindcss/forms`      | Form element reset & styling     |
| `@tailwindcss/aspect-ratio`| Aspect ratio utilities          |

---

## Quick Reference

### Commonly Used Patterns

```tsx
{/* Page layout */}
<div className="container section-spacing">
  <h1 className="responsive-heading-xl">Title</h1>
  <div className="grid-dashboard-cards">
    <div className="card hover-lift">...</div>
  </div>
</div>

{/* Form */}
<div className="grid-form-2col">
  <div className="form-group">
    <label className="label-text">Name</label>
    <input className="focus-ring-inset" />
  </div>
</div>
<div className="form-actions">
  <button className="btn">Submit</button>
</div>

{/* Table */}
<div className="table-responsive">
  <table>
    <th className="col-priority-4">Notes</th>
  </table>
</div>

{/* Loading */}
<div className="animate-pulse bg-muted h-4 rounded" />
<svg className="animate-spin h-5 w-5" />

{/* Print */}
<nav className="no-print">...</nav>
<div className="print-invoice print-no-break">...</div>
```
