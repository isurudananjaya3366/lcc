import type { MenuItem } from '@/config/navigation-menu';

/**
 * Check whether a route path matches the current pathname.
 *  - Exact: `/dashboard` === `/dashboard`
 *  - Prefix: `/inventory/products/123` starts with `/inventory`
 */
export function isRouteActive(pathname: string, href?: string): boolean {
  if (!href) return false;
  if (pathname === href) return true;
  // Prefix match for parent highlighting (e.g. /sales matches /sales/orders)
  if (href !== '/' && pathname.startsWith(href + '/')) return true;
  return false;
}

/**
 * Return true if a menu item (or any of its children) corresponds to the
 * current route.
 */
export function isMenuItemActive(pathname: string, item: MenuItem): boolean {
  if (isRouteActive(pathname, item.path)) return true;
  if (item.children) {
    return item.children.some((child) => isMenuItemActive(pathname, child));
  }
  return false;
}

/**
 * Check whether a user has the required permission(s) for a menu item.
 *
 * @param permission — the item's `permission` field (string | string[])
 * @param hasPermission — a function resolving a single permission key
 */
export function checkMenuItemPermission(
  permission: string | string[] | undefined,
  hasPermission: (p: string) => boolean
): boolean {
  if (!permission) return true; // no restriction
  if (typeof permission === 'string') return hasPermission(permission);
  // Array → require ANY match
  return permission.some((p) => hasPermission(p));
}

/**
 * Filter a list of menu items, keeping only those the user can access.
 * Groups are kept if at least one child is accessible.
 */
export function filterMenuByPermissions(
  items: MenuItem[],
  hasPermission: (p: string) => boolean
): MenuItem[] {
  return items.reduce<MenuItem[]>((acc, item) => {
    if (!checkMenuItemPermission(item.permission, hasPermission)) return acc;

    if (item.children) {
      const visibleChildren = item.children.filter((child) =>
        checkMenuItemPermission(child.permission, hasPermission)
      );
      if (visibleChildren.length === 0) return acc;
      acc.push({ ...item, children: visibleChildren });
    } else {
      acc.push(item);
    }
    return acc;
  }, []);
}

// ── Route → Breadcrumb label mapping ───────────────────────────

const routeToLabelMap: Record<string, string> = {
  dashboard: 'Dashboard',
  products: 'Products',
  categories: 'Categories',
  attributes: 'Attributes',
  variants: 'Variants',
  inventory: 'Inventory',
  warehouses: 'Warehouses',
  'stock-movements': 'Stock Movements',
  adjustments: 'Adjustments',
  transfers: 'Transfers',
  sales: 'Sales',
  orders: 'Orders',
  invoices: 'Invoices',
  quotations: 'Quotations',
  returns: 'Returns',
  pos: 'Point of Sale',
  sessions: 'Sessions',
  transactions: 'Transactions',
  receipts: 'Receipts',
  customers: 'Customers',
  vendors: 'Vendors',
  contacts: 'Contacts',
  leads: 'Leads',
  hr: 'Human Resources',
  employees: 'Employees',
  departments: 'Departments',
  attendance: 'Attendance',
  payroll: 'Payroll',
  leaves: 'Leave Management',
  accounting: 'Accounting',
  'journal-entries': 'Journal Entries',
  'chart-of-accounts': 'Chart of Accounts',
  reports: 'Reports',
  settings: 'Settings',
  profile: 'Profile',
  company: 'Company Settings',
  users: 'User Management',
  roles: 'Roles & Permissions',
  integrations: 'Integrations',
  preferences: 'Preferences',
  system: 'System',
  purchasing: 'Purchasing',
  bills: 'Bills',
  payments: 'Payments',
  new: 'New',
  edit: 'Edit',
  view: 'View',
  details: 'Details',
};

/**
 * Convert a URL segment to a human-readable label.
 */
export function getRouteLabel(segment: string): string {
  if (routeToLabelMap[segment]) return routeToLabelMap[segment];
  // Fallback: capitalize and replace hyphens
  return segment
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Detect if a URL segment looks like a dynamic ID.
 */
export function isDynamicSegment(segment: string): boolean {
  if (/^\d+$/.test(segment)) return true;
  if (/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(segment)) return true;
  if (/^[a-z]+_\d+$/.test(segment)) return true;
  return false;
}
