# Storefront Layout Documentation

## Overview

The storefront layout system provides a modular, responsive, and accessible layout for the LankaCommerce e-commerce frontend. Built with Next.js 15 App Router, Tailwind CSS, and Zustand for state management.

## Architecture

```
StoreLayout
├── SkipToContent
├── AnnouncementBar
├── Header (sticky)
│   ├── Logo
│   ├── DesktopNav + MegaMenu
│   ├── HeaderSearch / SearchOverlay
│   └── HeaderActions (Account, Cart, Wishlist)
├── MobileDrawer
│   ├── DrawerHeader
│   ├── MobileSearch
│   ├── MobileNavList
│   ├── MobileAccountLinks
│   └── MobileContactInfo
├── MainContent (children)
├── Footer
│   ├── FooterTop (Logo, Links, Newsletter, Social)
│   └── FooterBottom (Copyright, PaymentIcons)
├── FloatingContainer
│   ├── ScrollToTop
│   └── WhatsAppButton
└── CookieConsent
```

## Layout Structure

The `StoreLayout` component wraps all storefront pages using the Next.js `(storefront)/layout.tsx` route group (no URL prefix).

```tsx
import { StoreLayout } from '@/components/storefront/layout';

export default function StorefrontLayout({ children }) {
  return <StoreLayout>{children}</StoreLayout>;
}
```

## Component Groups

### Group A — Layout Shell (Tasks 01-14)

| Component | Description |
|-----------|-------------|
| `LayoutContainer` | Responsive max-width container |
| `AnnouncementBar` | Dismissible announcement with CTA |
| `MainContent` | Semantic `<main>` wrapper |
| `SkipToContent` | Accessible skip-to-main link |
| `FooterPlaceholder` | Dev placeholder for footer |
| `LayoutAnimationWrapper` | Fade-in animation wrapper |

**Hooks:**
- `useScrollPosition` — RAF-throttled scroll tracking
- `useStickyHeader` — Three behavior modes (always, hide-on-scroll, smart)

**Store:**
- `useStoreUIStore` — Zustand store for mobile menu, search overlay, cart drawer state
- Announcement store — Persist dismissed state for 30 days

### Group B — Header Components (Tasks 15-34)

| Component | Description |
|-----------|-------------|
| `Header` | Main header orchestrator with sticky behavior |
| `Logo` | Text fallback "Lanka"+"Commerce", responsive |
| `HeaderContainer` | Flex container with max-width |
| `HeaderSearch` | Desktop search bar |
| `SearchIconButton` | Mobile search toggle |
| `SearchOverlay` | Full-screen search overlay |
| `AccountLink` | User icon with login link |
| `AccountDropdown` | Auth-aware account menu |
| `LoginRegisterLinks` | Guest: Sign In + Register |
| `LoggedInMenu` | Authenticated: Profile, Orders, etc. |
| `CartIcon` | Shopping cart with badge |
| `CartBadge` | Item count badge (max "99+") |
| `MiniCart` | Cart dropdown with items |
| `MiniCartItem` | Individual cart item row |
| `MiniCartFooter` | Subtotal + action buttons |
| `WishlistIcon` | Heart icon, desktop only |
| `HeaderActions` | Action buttons container |

### Group C — Navigation & Mega Menu (Tasks 35-52)

| Component | Description |
|-----------|-------------|
| `DesktopNav` | Horizontal navigation bar |
| `NavItem` | Navigation item with hover delay |
| `NavLink` | Active-state-aware link |
| `SubmenuIndicator` | Chevron with rotation animation |
| `MegaMenu` | Absolute-positioned mega menu |
| `MegaMenuPanel` | Categories (75%) + Featured (25%) |
| `MegaMenuCategories` | 3-column category grid |
| `CategoryColumn` | Category title + subcategory links |
| `MegaMenuFeatured` | Featured image and CTA |
| `FeaturedImage` | Optimized Next.js Image |

**Hooks:**
- `useHoverDelay` — 100ms open / 200ms close delay
- `useNavigation` — TanStack Query data fetching

### Group D — Mobile Navigation (Tasks 53-68)

| Component | Description |
|-----------|-------------|
| `MobileMenuButton` | Hamburger toggle (md:hidden) |
| `HamburgerIcon` | Animated hamburger → X |
| `MobileDrawer` | Slide-in drawer with scroll lock |
| `DrawerBackdrop` | Semi-transparent overlay |
| `DrawerHeader` | Logo + close button |
| `CloseDrawerButton` | 44×44px touch target |
| `MobileSearch` | Full-width search input |
| `MobileNavList` | Accordion navigation |
| `MobileNavItem` | Collapsible nav item |
| `MobileAccountLinks` | Auth/guest account links |
| `MobileContactInfo` | Phone, WhatsApp, hours |

### Group E — Footer Components (Tasks 69-82)

| Component | Description |
|-----------|-------------|
| `Footer` | Main footer orchestrator |
| `FooterContainer` | Max-width container |
| `FooterTop` | 12-column grid layout |
| `FooterLogo` | Brand, description, address |
| `FooterLinks` | 4 link columns |
| `FooterLinkColumn` | Collapsible on mobile |
| `FooterLink` | Internal/external link detection |
| `FooterNewsletter` | Newsletter signup section |
| `NewsletterForm` | Email validation + API submit |
| `FooterSocial` | Social media links |
| `SocialIconLink` | Animated icon link |
| `FooterBottom` | Copyright + payment icons |
| `Copyright` | Dynamic year |
| `PaymentIcons` | Visa, MC, PayHere, COD, Bank |

### Group F — Floating Elements (Tasks 83-94)

| Component | Description |
|-----------|-------------|
| `WhatsAppButton` | Fixed bottom-right chat button |
| `ScrollToTop` | Scroll-to-top (appears after 400px) |
| `FloatingContainer` | Container for floating buttons |
| `CookieConsent` | Cookie consent banner |

## Props Reference

### WhatsAppButton

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `phoneNumber` | `string` | Yes | — | Business phone number |
| `message` | `string` | No | "Hello! I'm interested..." | Pre-filled message |
| `className` | `string` | No | — | Additional CSS classes |

### ScrollToTop

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `showAfter` | `number` | No | `400` | Scroll threshold in px |
| `className` | `string` | No | — | Additional CSS classes |

### CookieConsent

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `privacyPolicyUrl` | `string` | No | `/privacy` | Privacy policy link |
| `cookiePolicyUrl` | `string` | No | `/cookies` | Cookie policy link |
| `onAccept` | `() => void` | No | — | Callback on accept |
| `onReject` | `() => void` | No | — | Callback on reject |

## Usage Examples

### Basic Layout

```tsx
import { StoreLayout } from '@/components/storefront/layout';

export default function Layout({ children }) {
  return <StoreLayout>{children}</StoreLayout>;
}
```

### Individual Components

```tsx
import {
  Header,
  Footer,
  FloatingContainer,
  CookieConsent,
} from '@/components/storefront/layout';
```

### WhatsApp Integration

```tsx
<FloatingContainer
  whatsappNumber="0771234567"
  whatsappMessage="Hi, I need help with my order"
  scrollThreshold={300}
/>
```

## Customization

### Theme Colors
- Primary green: `green-700` (navigation active states)
- WhatsApp green: `#25D366`
- Cart badge: `red-600`
- Footer background: `gray-900` (top), `gray-800` (bottom)
- Cookie banner: `gray-800`

### Breakpoints
- Mobile: < 768px (md)
- Desktop: ≥ 768px
- Large desktop: ≥ 1024px (lg)
- Max content width: `max-w-7xl` (1280px)

### Currency
- LKR (₨) — Sri Lankan Rupee
- Free shipping threshold: ₨5,000
- VAT: 8%

## Accessibility

### Keyboard Navigation
- **Tab**: Navigate between interactive elements
- **Enter/Space**: Activate buttons and links
- **Escape**: Close overlays, drawers, and dropdowns

### Screen Reader
- All images have `alt` text
- Interactive elements have `aria-label`
- Landmarks: `role="banner"`, `role="navigation"`, `role="main"`, `role="contentinfo"`
- Live regions for dynamic content (cart count, announcements)

### Skip Links
- "Skip to content" link appears on first Tab press
- Bypasses header/navigation for keyboard users

### Focus Management
- Focus trap in mobile drawer
- Auto-focus on search overlay open
- Visible focus indicators on all interactive elements

## API Integration

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/storefront/navigation` | GET | Navigation menu data |
| `/api/newsletter/subscribe` | POST | Newsletter signup |

## Troubleshooting

### Common Issues

**AnnouncementBar won't dismiss**
- Check localStorage is available
- Verify announcement store persistence config

**MegaMenu not showing**
- Ensure navigation data is loaded (check TanStack Query)
- Verify hover delay timing

**Mobile drawer not scrolling**
- Body scroll lock may conflict with other modals
- Check z-index stacking

**Cookie consent reappearing**
- localStorage may be cleared
- Check consent expiry (365 days)
- Verify `lcc-cookie-consent` key exists
