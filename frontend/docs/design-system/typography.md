# LankaCommerce Cloud — Typography System

> **Version:** 1.0  
> **Last Updated:** 2025-07-20

## Overview

The typography system uses **Inter** as the primary font, loaded via `next/font/google` with automatic self-hosting, zero layout shift, and font-display: swap. All font scales are defined in `tailwind.config.ts` with paired line heights.

## Font Families

| Utility | Font Stack | Usage |
|---------|-----------|-------|
| `font-sans` | Inter → system fallbacks | Body text, UI elements |
| `font-mono` | SF Mono → Consolas → system mono | Code, data tables |
| `font-display` | Inter → system fallbacks | Headings (if varied) |

### Fallback Stack (sans)

```
Inter → -apple-system → BlinkMacSystemFont → "Segoe UI" →
Roboto → "Noto Sans" → "Helvetica Neue" → Arial → sans-serif
```

Noto Sans is included for Sinhala and Tamil script support.

## Font Size Scale

| Token | Size | Line Height | Utility | Usage |
|-------|------|-------------|---------|-------|
| xs | 0.75rem (12px) | 1rem (16px) | `text-xs` | Captions, metadata |
| sm | 0.875rem (14px) | 1.25rem (20px) | `text-sm` | Labels, secondary text |
| base | 1rem (16px) | 1.5rem (24px) | `text-base` | Body text (default) |
| lg | 1.125rem (18px) | 1.75rem (28px) | `text-lg` | Lead paragraphs, H6 |
| xl | 1.25rem (20px) | 1.75rem (28px) | `text-xl` | H5, card titles |
| 2xl | 1.5rem (24px) | 2rem (32px) | `text-2xl` | H4 |
| 3xl | 1.875rem (30px) | 2.25rem (36px) | `text-3xl` | H3 |
| 4xl | 2.25rem (36px) | 2.5rem (40px) | `text-4xl` | H2 |
| 5xl | 3rem (48px) | 1 (48px) | `text-5xl` | H1 |
| 6xl | 3.75rem (60px) | 1 (60px) | `text-6xl` | Display headings |
| 7xl+ | 4.5–8rem | 1 | `text-7xl`+ | Hero sections |

## Font Weights

| Token | Value | Utility | Usage |
|-------|-------|---------|-------|
| light | 300 | `font-light` | Subtle text |
| normal | 400 | `font-normal` | Body text |
| medium | 500 | `font-medium` | Emphasis, H5-H6 |
| semibold | 600 | `font-semibold` | H3-H4, labels |
| bold | 700 | `font-bold` | H1-H2, strong emphasis |

## Letter Spacing

| Token | Value | Utility | Usage |
|-------|-------|---------|-------|
| tighter | -0.05em | `tracking-tighter` | Display headings |
| tight | -0.025em | `tracking-tight` | Headings |
| normal | 0 | `tracking-normal` | Body text |
| wide | 0.025em | `tracking-wide` | Small caps |
| wider | 0.05em | `tracking-wider` | Uppercase labels |
| widest | 0.1em | `tracking-widest` | All-caps text |

## Heading Styles (Base Layer)

Headings are styled in `@layer base` in `globals.css`:

| Level | Size | Weight | Line Height | Tracking |
|-------|------|--------|-------------|----------|
| H1 | `text-5xl` (48px) | bold | tight (1.25) | tight |
| H2 | `text-4xl` (36px) | bold | tight (1.25) | tight |
| H3 | `text-3xl` (30px) | semibold | snug (1.375) | tight |
| H4 | `text-2xl` (24px) | semibold | snug (1.375) | normal |
| H5 | `text-xl` (20px) | medium | snug (1.375) | normal |
| H6 | `text-lg` (18px) | medium | snug (1.375) | normal |

## Body & Text Classes

| Class | Size | Weight | Color | Usage |
|-------|------|--------|-------|-------|
| (body default) | base | normal | foreground | Page body |
| `.caption` | sm | normal | secondary-600 | Captions, metadata |
| `.small-text` | xs | normal | secondary-500 | Footnotes, fine print |
| `.text-muted` | inherit | normal | secondary-600 | De-emphasized text |
| `.label-text` | sm | medium | secondary-700 | Form labels, tags |
| `.label-text-uppercase` | xs | semibold | secondary-700 | Section headers |

All classes support dark mode automatically.

## Prose (Rich Content)

The `@tailwindcss/typography` plugin is customized in `tailwind.config.ts`:

```tsx
<article className="prose dark:prose-invert max-w-none">
  {/* Markdown or rich HTML content */}
</article>
```

Prose colors map to the design system's CSS variables (primary for links, secondary for text).

## Text Truncation

| Utility | Lines | Usage |
|---------|-------|-------|
| `truncate` | 1 | Single-line ellipsis (Tailwind built-in) |
| `line-clamp-1` | 1 | Single-line via -webkit-line-clamp |
| `line-clamp-2` | 2 | Card titles, short descriptions |
| `line-clamp-3` | 3 | Product descriptions |
| `line-clamp-4` | 4 | Blog excerpts |
| `line-clamp-5` | 5 | Detailed previews |
| `line-clamp-none` | ∞ | Remove clamping at responsive breakpoints |

## Accessibility

- Minimum body text: 16px (`text-base`)
- Minimum small text: 12px (`text-xs`) — only for metadata
- All sizes use `rem` for browser zoom support
- Heading contrast meets WCAG AAA
- Font-display: swap prevents invisible text (FOIT)
