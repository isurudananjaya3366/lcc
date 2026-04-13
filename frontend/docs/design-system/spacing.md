# LankaCommerce Cloud — Spacing & Layout System

> **Version:** 1.0  
> **Last Updated:** 2025-07-20

## Overview

The spacing system uses a **4px base unit** (0.25rem). All spacing values are multiples of this unit, extended with fractional values for fine control. The system covers spacing, containers, border radius, shadows, z-index, and layout grids.

## Spacing Scale

| Key | Value | Pixels | Usage |
|-----|-------|--------|-------|
| 0.5 | 0.125rem | 2px | Minimal gap |
| 1 | 0.25rem | 4px | Very tight |
| 1.5 | 0.375rem | 6px | Subtle separation |
| 2 | 0.5rem | 8px | Small spacing |
| 2.5 | 0.625rem | 10px | Compact elements |
| 3 | 0.75rem | 12px | Medium-small |
| 3.5 | 0.875rem | 14px | Between small & standard |
| 4 | 1rem | 16px | Standard spacing |
| 5 | 1.25rem | 20px | Medium |
| 6 | 1.5rem | 24px | Cards, panels |
| 8 | 2rem | 32px | Large spacing |
| 10 | 2.5rem | 40px | Section spacing |
| 12 | 3rem | 48px | Component spacing |
| 16 | 4rem | 64px | Layout spacing |
| 18 | 4.5rem | 72px | Extended |
| 20 | 5rem | 80px | Large layout |
| 22 | 5.5rem | 88px | Extended |
| 24 | 6rem | 96px | Extra large |

## Container

Containers are centered with responsive padding:

| Breakpoint | Max Width | Padding |
|------------|-----------|---------|
| default | 100% | 1rem |
| sm (640px) | 640px | 1rem |
| md (768px) | 768px | 1.5rem |
| lg (1024px) | 1024px | 2rem |
| xl (1280px) | 1280px | 2rem |
| 2xl (1536px) | 1536px | 2rem |

## Border Radius

| Class | Value | Usage |
|-------|-------|-------|
| `rounded-none` | 0 | Sharp edges |
| `rounded-sm` | 0.125rem (2px) | Subtle rounding |
| `rounded` | 0.375rem (6px) | Buttons, inputs |
| `rounded-lg` | 0.5rem (8px) | Cards |
| `rounded-xl` | 0.75rem (12px) | Large cards |
| `rounded-2xl` | 1rem (16px) | Modals |
| `rounded-3xl` | 1.5rem (24px) | Hero sections |
| `rounded-full` | 9999px | Avatars, pills |

## Box Shadows

| Class | Usage |
|-------|-------|
| `shadow-sm` | Subtle elevation, inputs |
| `shadow` | Standard buttons, elements |
| `shadow-md` | Hover states, tooltips |
| `shadow-lg` | Cards, dropdowns |
| `shadow-xl` | Dialogs, popovers |
| `shadow-2xl` | Modals, floating elements |
| `shadow-inner` | Pressed states, wells |

### Component Shadow Utilities

| Class | Maps To | Usage |
|-------|---------|-------|
| `.shadow-card` | shadow-lg | Default card |
| `.shadow-card-elevated` | shadow-xl | Featured card |
| `.shadow-card-subtle` | shadow-md | Flat card |
| `.shadow-card-flat` | none | Borderless card |
| `.shadow-modal` | shadow-2xl | Modal dialog |
| `.shadow-dialog` | shadow-xl | Lightweight dialog |
| `.shadow-popover` | shadow-xl | Popovers |
| `.shadow-sheet` | shadow-2xl | Bottom sheets |

## Z-Index Scale

| Utility | Value | Usage |
|---------|-------|-------|
| `z-dropdown` | 50 | Dropdown menus |
| `z-sticky` | 100 | Sticky headers |
| `z-fixed` | 150 | Fixed elements |
| `z-modal-backdrop` | 200 | Modal overlay |
| `z-modal` | 250 | Modal content |
| `z-popover` | 300 | Popovers |
| `z-tooltip` | 350 | Tooltips |
| `z-toast` | 400 | Notifications |

## Layout Grid Utilities

| Class | Columns | Gap | Responsive |
|-------|---------|-----|------------|
| `.grid-dashboard-cards` | auto-fit, min 280px | 24px | Auto-reflow |
| `.grid-dashboard-widgets` | 12 fixed | 16px | Use col-span |
| `.grid-form-2col` | 2 | 16px | 1 col on mobile |
| `.grid-form-3col` | 3 | 16px | 1 col on mobile |
| `.grid-stats` | 4→2→1 | 16px | Breakpoint-based |

## Section Spacing

| Class | Padding |
|-------|---------|
| `.section-spacing-sm` | py-8 / md:py-10 / lg:py-12 |
| `.section-spacing` | py-12 / md:py-16 / lg:py-20 |
| `.section-spacing-lg` | py-16 / md:py-20 / lg:py-24 |

## Form Layout

| Class | Description |
|-------|-------------|
| `.form-group` | mb-4 wrapper for label + input |
| `.form-group-inline` | Flex row with centered gap-3 |
| `.form-actions` | Right-aligned button row with gap-2 |
