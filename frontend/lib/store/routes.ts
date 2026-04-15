/**
 * Store Routes Configuration
 *
 * All storefront route paths organized by category.
 */

export const storeRoutes = {
  home: '/',

  // Product routes
  products: {
    list: '/products',
    detail: (slug: string) => `/products/${slug}`,
    category: (slug: string) => `/search?category=${slug}`,
    brand: (slug: string) => `/search?brand=${slug}`,
    sale: '/search?category=deals',
    newArrivals: '/search?sort=newest',
    bestSellers: '/search?sort=popular',
  },

  // Cart & wishlist
  cart: {
    view: '/cart',
    wishlist: '/account',
    compare: '/search',
  },

  // Checkout
  checkout: {
    index: '/checkout',
    shipping: '/checkout',
    payment: '/checkout',
    confirmation: '/checkout',
    success: '/checkout',
  },

  // Account
  account: {
    index: '/account',
    orders: '/account',
    profile: '/account',
    addresses: '/account',
  },

  // Auth
  auth: {
    login: '/login',
    register: '/register',
    forgotPassword: '/forgot-password',
    resetPassword: (token: string) => `/reset-password/${token}`,
  },

  // Content pages
  content: {
    about: '/about',
    contact: '/contact',
    faq: '/faq',
    blog: '/blog',
    blogPost: (slug: string) => `/blog/${slug}`,
  },

  // Legal
  legal: {
    terms: '/terms',
    privacy: '/privacy',
    returns: '/returns',
    shippingPolicy: '/shipping-policy',
    cookies: '/cookies',
  },

  // Search
  search: '/search',
} as const;

/** Get a route by dot-separated key */
export function getRoute(key: string): string {
  const parts = key.split('.');
  let current: unknown = storeRoutes;
  for (const part of parts) {
    if (current && typeof current === 'object' && part in current) {
      current = (current as Record<string, unknown>)[part];
    } else {
      return '/';
    }
  }
  return typeof current === 'string' ? current : '/';
}

/** Build breadcrumb items from a path */
export function generateBreadcrumbs(pathname: string): Array<{ label: string; href: string }> {
  const segments = pathname.split('/').filter(Boolean);
  const breadcrumbs: Array<{ label: string; href: string }> = [{ label: 'Home', href: '/' }];

  let currentPath = '';
  for (const segment of segments) {
    currentPath += `/${segment}`;
    const label = segment.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
    breadcrumbs.push({ label, href: currentPath });
  }

  return breadcrumbs;
}
