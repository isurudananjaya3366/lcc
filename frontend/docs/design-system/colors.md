# LankaCommerce Cloud — Color System

> **Version:** 1.0  
> **Last Updated:** 2025-07-20

## Overview

The color system uses CSS custom properties (HSL format without the `hsl()` wrapper) to enable:

- Theme switching via `.dark` class on `<html>`
- Tailwind opacity modifiers (e.g., `bg-primary/50`)
- Runtime theming without rebuilds

All variables are defined in `styles/variables.css` and mapped to Tailwind utilities in `tailwind.config.ts`.

## Color Architecture

```
:root (Light Theme)
├── Color Palettes (50–950 shades)
│   ├── Primary (Blue)     — Brand, CTAs, links
│   ├── Secondary (Slate)  — Neutral, borders, text
│   ├── Success (Green)    — Positive states
│   ├── Warning (Amber)    — Caution states
│   ├── Error (Red)        — Negative states
│   └── Info (Cyan)        — Informational states
├── Semantic Colors
│   ├── Backgrounds (background, card, popover, muted, accent)
│   ├── Foregrounds (foreground, card-foreground, muted-foreground)
│   └── Borders (border, input, ring)
├── Chart Colors (chart-1 through chart-5)
└── Status Colors (pending, processing, completed, etc.)

.dark (Dark Theme)
└── Overrides for all semantic colors
```

## Color Palettes

### Primary (Blue) — `--primary-{shade}`

| Shade | HSL | Usage |
|-------|-----|-------|
| 50 | 221 100% 97% | Subtle backgrounds |
| 100–200 | … | Hover states, borders |
| 500 | 221 83% 53% | **Default brand color** |
| 600–700 | … | Hover/active states |
| 950 | 221 83% 20% | Strong text |

### Secondary (Slate) — `--secondary-{shade}`

Neutral palette for text, borders, and surfaces.

### State Palettes

| Palette | Hue | Default (500) |
|---------|-----|---------------|
| Success | 142° (green) | 142 71% 45% |
| Warning | 38° (amber) | 38 92% 50% |
| Error | 0° (red) | 0 84% 60% |
| Info | 199° (cyan) | 199 89% 48% |

## Semantic Colors

| Variable | Light | Dark | Usage |
|----------|-------|------|-------|
| `--background` | white | secondary-950 | Page canvas |
| `--foreground` | secondary-950 | secondary-50 | Body text |
| `--card` | white | secondary-900 | Card surfaces |
| `--muted` | slate-100 | secondary-800 | Subtle areas |
| `--border` | secondary-200 | secondary-800 | Separators |
| `--ring` | primary-500 | primary-400 | Focus rings |

## Usage Guidelines

### Tailwind Utilities

```tsx
// Semantic surface
<div className="bg-background text-foreground" />

// Brand palette with shade
<button className="bg-primary-600 hover:bg-primary-700 text-primary-foreground" />

// State colors
<span className="text-success">Saved</span>
<span className="text-error">Failed</span>

// Status badges
<span className="bg-status-pending text-white" />

// Chart series
<div className="bg-chart-1" />
```

### CSS Variable Access

```css
.custom {
  color: hsl(var(--primary-500));
  border-color: hsl(var(--border));
}
```

## Accessibility

- All foreground/background pairs meet WCAG AA (4.5:1 contrast)
- Focus rings use `--ring` (primary brand color)
- Chart palette designed to be distinguishable for color-vision deficiency

## Status Colors

| Status | Variable | Maps To |
|--------|----------|---------|
| Pending | `--status-pending` | warning-500 |
| Processing | `--status-processing` | info-500 |
| Completed | `--status-completed` | success-500 |
| Cancelled | `--status-cancelled` | secondary-400 |
| Failed | `--status-failed` | error-500 |
| Draft | `--status-draft` | secondary-300 |
| Archived | `--status-archived` | secondary-500 |
| New | `--status-new` | primary-500 |

## Adding New Colors

1. Add HSL variable in `styles/variables.css` under `:root` and `.dark`
2. Map to Tailwind in `tailwind.config.ts` → `theme.extend.colors`
3. Update this documentation
