# Animations & Transitions

LankaCommerce Cloud provides a comprehensive animation system with CSS keyframes, Tailwind animation utilities, and transition duration/timing scales.

---

## Transition Duration Scale

Available via `duration-*` Tailwind classes:

| Class          | Duration | Usage              |
| -------------- | -------- | ------------------ |
| `duration-75`  | 75ms     | Instant feedback   |
| `duration-100` | 100ms    | Quick transitions  |
| `duration-150` | 150ms    | Default            |
| `duration-200` | 200ms    | Standard           |
| `duration-300` | 300ms    | Deliberate         |
| `duration-500` | 500ms    | Slow emphasis      |

```tsx
<button className="transition-colors duration-200 hover:bg-primary">
  Click me
</button>
```

---

## Transition Timing Functions

Available via `ease-*` Tailwind classes:

| Class          | Value                          | Usage            |
| -------------- | ------------------------------ | ---------------- |
| `ease-in`      | `cubic-bezier(0.4, 0, 1, 1)`  | Exit animations  |
| `ease-out`     | `cubic-bezier(0, 0, 0.2, 1)`  | Enter animations |
| `ease-in-out`  | `cubic-bezier(0.4, 0, 0.2, 1)`| Transitions      |

```tsx
<div className="transition-transform duration-200 ease-out hover:scale-105">
  Card
</div>
```

---

## Animation Keyframes

### Tailwind Utilities

Use `animate-*` classes directly in JSX:

| Class                  | Animation      | Duration | Usage               |
| ---------------------- | -------------- | -------- | ------------------- |
| `animate-fade-in`      | Fade in        | 200ms    | Modal/popover enter |
| `animate-fade-out`     | Fade out       | 200ms    | Modal/popover exit  |
| `animate-slide-in-up`  | Slide up       | 200ms    | Toast notifications |
| `animate-slide-in-down`| Slide down     | 200ms    | Dropdown menus      |
| `animate-slide-in-left`| Slide left     | 200ms    | Sidebar appearance  |
| `animate-slide-in-right`| Slide right   | 200ms    | Sheet appearance    |
| `animate-scale-in`     | Scale in       | 200ms    | Modal zoom effect   |
| `animate-spin`         | Continuous spin| 1s       | Loading spinners    |
| `animate-pulse`        | Pulsing opacity| 2s       | Skeleton loaders    |
| `animate-shake`        | Error shake    | 500ms    | Form validation     |

```tsx
{/* Toast notification */}
<div className="animate-slide-in-up">New order received</div>

{/* Loading spinner */}
<svg className="animate-spin h-5 w-5">...</svg>

{/* Skeleton loader */}
<div className="animate-pulse bg-muted h-4 rounded" />

{/* Error shake */}
<input className={hasError ? 'animate-shake border-error' : ''} />
```

### CSS Utility Classes

Also available as CSS classes from `animations.css`:

| Class                   | Keyframe    | Timing                       |
| ----------------------- | ----------- | ---------------------------- |
| `.animate-fade-in`      | `fadeIn`    | Uses `--duration-default`    |
| `.animate-fade-out`     | `fadeOut`   | Uses `--duration-default`    |
| `.animate-slide-up`     | `slideUp`   | Uses `--duration-default`    |
| `.animate-slide-down`   | `slideDown` | Uses `--duration-default`    |
| `.animate-slide-left`   | `slideLeft` | Uses `--duration-default`    |
| `.animate-slide-right`  | `slideRight`| Uses `--duration-default`    |
| `.animate-scale-in`     | `scaleIn`   | Uses `--duration-default`    |
| `.animate-spin`         | `spin`      | 1s linear infinite           |
| `.animate-pulse`        | `pulse`     | 2s ease-in-out infinite      |
| `.animate-shake`        | `shake`     | 500ms ease-in-out            |
| `.animate-shimmer`      | `shimmer`   | 1.5s infinite (skeleton bg)  |

---

## Reduced Motion

All animations respect `prefers-reduced-motion: reduce`. Users with motion sensitivity see instant transitions:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

No additional code needed — this is applied globally via `animations.css`.

---

## Common Patterns

### Page Transitions

```tsx
<main className="animate-fade-in">
  {children}
</main>
```

### Modal Entry

```tsx
<div className="animate-scale-in">
  <Dialog>...</Dialog>
</div>
```

### Sidebar Slide

```tsx
<aside className="animate-slide-in-left">
  <Navigation />
</aside>
```

### Hover Effects

```tsx
<div className="transition-all duration-200 ease-out hover:shadow-lg hover:-translate-y-0.5">
  <Card />
</div>
```

### Interactive Elements

Use the `.interactive` utility for consistent hover/focus states:

```tsx
<button className="interactive">Menu Item</button>
```

Use `.hover-lift` for elevation on hover:

```tsx
<div className="hover-lift">
  <Card />
</div>
```

---

## Best Practices

1. **Use `duration-200`** as the default transition speed
2. **Use `ease-out`** for enter animations, `ease-in` for exits
3. **Keep animations under 300ms** for UI interactions
4. **Never animate `width`/`height`** — use `transform: scale()` instead
5. **Test with reduced motion** enabled in OS accessibility settings
6. **Use `will-change`** sparingly for complex animations on known elements
