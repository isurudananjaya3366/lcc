/**
 * Store Navigation Configuration
 *
 * Main navigation menus for header, mobile, and footer.
 */

export interface NavItem {
  label: string;
  href: string;
  children?: NavItem[];
  icon?: string;
}

/** Main header navigation */
export const mainNavigation: NavItem[] = [
  { label: 'Home', href: '/' },
  {
    label: 'Shop',
    href: '/products',
    children: [
      { label: 'All Products', href: '/products' },
      { label: 'New Arrivals', href: '/search?sort=newest' },
      { label: 'Best Sellers', href: '/search?sort=popular' },
      { label: 'Deals & Sale', href: '/search?category=deals' },
    ],
  },
  {
    label: 'Categories',
    href: '/search',
    children: [
      { label: 'Electronics', href: '/search?category=electronics' },
      { label: 'Fashion', href: '/search?category=fashion' },
      { label: 'Home & Garden', href: '/search?category=home' },
      { label: 'Health & Beauty', href: '/search?category=health' },
      { label: 'Sports & Outdoors', href: '/search?category=sports' },
    ],
  },
  { label: 'Deals', href: '/search?category=deals' },
  { label: 'About', href: '/about' },
];

/** Footer navigation columns */
export const footerNavigation = {
  shop: {
    title: 'Shop',
    links: [
      { label: 'All Products', href: '/products' },
      { label: 'Categories', href: '/search' },
      { label: 'Deals & Sales', href: '/search?category=deals' },
      { label: 'New Arrivals', href: '/search?sort=newest' },
      { label: 'Best Sellers', href: '/search?sort=popular' },
    ],
  },
  customerService: {
    title: 'Customer Service',
    links: [
      { label: 'Help Center', href: '/help' },
      { label: 'Contact Us', href: '/contact' },
      { label: 'Shipping Info', href: '/shipping-policy' },
      { label: 'Returns & Exchanges', href: '/returns' },
      { label: 'Track Order', href: '/track' },
    ],
  },
  company: {
    title: 'Company',
    links: [
      { label: 'About Us', href: '/about' },
      { label: 'Our Story', href: '/about' },
      { label: 'Contact', href: '/contact' },
      { label: 'Careers', href: '/careers' },
      { label: 'Blog', href: '/blog' },
    ],
  },
} as const;

/** Account navigation */
export const accountNavigation: NavItem[] = [
  { label: 'My Account', href: '/account' },
  { label: 'Orders', href: '/account' },
  { label: 'Profile', href: '/account' },
  { label: 'Addresses', href: '/account' },
];
