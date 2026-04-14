# Responsive Design — Dashboard Layout

## Breakpoint Strategy

Mobile-first approach using Tailwind CSS breakpoints:

| Token | Width    | Description              |
|-------|----------|--------------------------|
| `xs`  | ≥ 475px  | Large phones             |
| `sm`  | ≥ 640px  | Small tablets             |
| `md`  | ≥ 768px  | Tablets (portrait)        |
| `lg`  | ≥ 1024px | **Primary desktop threshold** |
| `xl`  | ≥ 1280px | Large desktop             |
| `2xl` | ≥ 1536px | Wide desktop              |
| `3xl` | ≥ 1920px | Ultra-wide                |

**`lg` (1024px)** is the primary threshold that switches between mobile/tablet and desktop layouts.

## Sidebar Behaviour

| Viewport  | Sidebar                                   |
|-----------|-------------------------------------------|
| `< lg`    | Hidden. Replaced by slide-in drawer (MobileSidebar) triggered by header hamburger or right-swipe from left edge. |
| `≥ lg`    | Permanent. 240px expanded / 64px collapsed. Ctrl+B toggles. |

## Header Behaviour

| Element          | Mobile (`< md`)    | Tablet (`md`)      | Desktop (`≥ lg`)    |
|------------------|--------------------|--------------------|---------------------|
| Menu toggle      | Visible            | Visible            | Hidden              |
| Tenant switcher  | Hidden             | Hidden             | Visible             |
| Search           | Icon-only          | Icon-only (< md)   | Full bar (w-60/w-72)|
| Quick actions    | Available          | Available          | Available           |
| Help button      | Hidden             | Available          | Available           |
| Notifications    | Available          | Available          | Available           |
| User menu        | Available          | Available          | Full name + avatar  |

## Content Padding

| Breakpoint | Padding   | Tailwind class |
|------------|-----------|----------------|
| Base       | 16px      | `p-4`          |
| `md`       | 24px      | `md:p-6`       |
| `lg`       | 32px      | `lg:p-8`       |
| `xl`       | 40px      | `xl:p-10`      |

Content is limited to `max-w-screen-2xl` and auto-centred.

## Bottom Navigation (Mobile)

- Visible below `md` breakpoint (`md:hidden`)
- Fixed at bottom, 56px height
- 5 items: Dashboard, Products, +New (action button), Tasks, More
- Respects iOS safe area (`pb-[env(safe-area-inset-bottom)]`)
- Main content has `pb-16 md:pb-0` to avoid overlap

## Touch Interactions

- **Swipe right** from left edge (0–20px zone) opens mobile drawer
- **Swipe left** on drawer closes it
- Thresholds: 50px distance, 0.3px/ms velocity
- All interactive elements have 44×44px minimum touch targets
- No hover-dependent features on mobile

## Print Behaviour

- Sidebar, header, navigation, and buttons are hidden
- Content fills full width with no padding
- Black-and-white output, no shadows or gradients
- Tables maintain borders with page-break control
- A4 page size with 1-inch margins

## Hooks

| Hook                   | Returns                                         |
|------------------------|-------------------------------------------------|
| `useIsMobile()`        | `boolean` — viewport < 640px                    |
| `useIsTablet()`        | `boolean` — viewport 640–1023px                 |
| `useIsDesktop()`       | `boolean` — viewport ≥ 1024px                   |
| `useIsLargeDesktop()`  | `boolean` — viewport ≥ 1280px                   |
| `useIsUltraWide()`     | `boolean` — viewport ≥ 1920px                   |
| `useCurrentBreakpoint()`| `BreakpointName` — xs/sm/md/lg/xl/2xl/3xl      |
| `useMediaQuery(query)` | `boolean` — arbitrary CSS media query            |
| `useSwipeGesture()`    | Touch handlers for swipe detection               |
| `useSidebarState()`    | Sidebar state + mobile drawer controls           |
| `useLayout()`          | Combined layout state (sidebar + dimensions + breakpoints) |

## Testing Checklist

- [ ] 375px — Mobile drawer opens/closes, bottom nav visible, swipe works
- [ ] 768px — Drawer still active, search icon-only, bottom nav hidden
- [ ] 1024px — Sidebar permanent, toggle hidden, full search bar
- [ ] 1280px — Increased padding (40px), sidebar 240px/64px
- [ ] 1920px — Content centred within max-width
- [ ] All buttons/links have 44×44px touch targets
- [ ] Keyboard navigation works (Tab, Enter, Escape, Ctrl+B, Ctrl+K)
- [ ] `prefers-reduced-motion` disables animations
- [ ] Print preview hides chrome, shows content full-width
