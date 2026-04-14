import type { LucideIcon } from 'lucide-react';
import {
  LayoutDashboard,
  Package,
  FolderTree,
  Archive,
  RefreshCw,
  Truck,
  ShoppingCart,
  FileText,
  FileCheck,
  Users,
  CreditCard,
  ShoppingBag,
  Receipt,
  Building2,
  DollarSign,
  UserCircle,
  Clock,
  Wallet,
  Calendar,
  Settings,
  UserCog,
  Shield,
  Server,
  Sliders,
  BarChart3,
} from 'lucide-react';

// ── Types ──────────────────────────────────────────────────────

export interface MenuItem {
  id: string;
  label: string;
  icon: LucideIcon;
  path?: string;
  children?: MenuItem[];
  permission?: string | string[];
  badge?: number | string;
  divider?: boolean;
}

// ── Menu structure ─────────────────────────────────────────────

export const navigationMenuItems: MenuItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    path: '/dashboard',
  },
  {
    id: 'inventory',
    label: 'Inventory',
    icon: Package,
    permission: 'inventory.view',
    children: [
      {
        id: 'products',
        label: 'Products',
        icon: Package,
        path: '/inventory/products',
        permission: 'inventory.view_product',
      },
      {
        id: 'categories',
        label: 'Categories',
        icon: FolderTree,
        path: '/inventory/categories',
        permission: 'inventory.view_category',
      },
      {
        id: 'stock',
        label: 'Stock',
        icon: Archive,
        path: '/inventory/stock',
        permission: 'inventory.view_stock',
      },
      {
        id: 'adjustments',
        label: 'Adjustments',
        icon: RefreshCw,
        path: '/inventory/adjustments',
        permission: 'inventory.view_adjustment',
      },
      {
        id: 'suppliers',
        label: 'Suppliers',
        icon: Truck,
        path: '/inventory/suppliers',
        permission: 'inventory.view_supplier',
      },
    ],
  },
  {
    id: 'sales',
    label: 'Sales',
    icon: ShoppingCart,
    permission: 'sales.view',
    children: [
      {
        id: 'orders',
        label: 'Orders',
        icon: ShoppingCart,
        path: '/sales/orders',
        permission: 'sales.view_order',
      },
      {
        id: 'invoices',
        label: 'Invoices',
        icon: FileText,
        path: '/sales/invoices',
        permission: 'sales.view_invoice',
      },
      {
        id: 'quotes',
        label: 'Quotes',
        icon: FileCheck,
        path: '/sales/quotes',
        permission: 'sales.view_quote',
      },
      {
        id: 'customers',
        label: 'Customers',
        icon: Users,
        path: '/sales/customers',
        permission: 'sales.view_customer',
      },
      {
        id: 'pos',
        label: 'POS',
        icon: CreditCard,
        path: '/sales/pos',
        permission: 'sales.view_pos',
      },
    ],
  },
  {
    id: 'purchasing',
    label: 'Purchasing',
    icon: ShoppingBag,
    permission: 'purchasing.view',
    children: [
      {
        id: 'purchase-orders',
        label: 'Purchase Orders',
        icon: ShoppingBag,
        path: '/purchasing/orders',
        permission: 'purchasing.view_order',
      },
      {
        id: 'bills',
        label: 'Bills',
        icon: Receipt,
        path: '/purchasing/bills',
        permission: 'purchasing.view_bill',
      },
      {
        id: 'vendors',
        label: 'Vendors',
        icon: Building2,
        path: '/purchasing/vendors',
        permission: 'purchasing.view_vendor',
      },
      {
        id: 'payments',
        label: 'Payments',
        icon: DollarSign,
        path: '/purchasing/payments',
        permission: 'purchasing.view_payment',
      },
    ],
  },
  {
    id: 'accounting',
    label: 'Accounting',
    icon: Receipt,
    path: '/accounting',
    permission: 'accounting.view',
  },
  {
    id: 'hr',
    label: 'HR',
    icon: UserCircle,
    permission: 'hr.view',
    children: [
      {
        id: 'employees',
        label: 'Employees',
        icon: Users,
        path: '/hr/employees',
        permission: 'hr.view_employee',
      },
      {
        id: 'attendance',
        label: 'Attendance',
        icon: Clock,
        path: '/hr/attendance',
        permission: 'hr.view_attendance',
      },
      {
        id: 'payroll',
        label: 'Payroll',
        icon: Wallet,
        path: '/hr/payroll',
        permission: 'hr.view_payroll',
      },
      {
        id: 'leave',
        label: 'Leave',
        icon: Calendar,
        path: '/hr/leave',
        permission: 'hr.view_leave',
      },
    ],
  },
  {
    id: 'reports',
    label: 'Reports',
    icon: BarChart3,
    path: '/reports',
    permission: 'reports.view',
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: Settings,
    permission: 'settings.view',
    divider: true,
    children: [
      {
        id: 'settings-users',
        label: 'Users',
        icon: UserCog,
        path: '/settings/users',
        permission: 'settings.manage_users',
      },
      {
        id: 'settings-roles',
        label: 'Roles',
        icon: Shield,
        path: '/settings/roles',
        permission: 'settings.manage_roles',
      },
      {
        id: 'settings-system',
        label: 'System',
        icon: Server,
        path: '/settings/system',
        permission: 'settings.manage_system',
      },
      {
        id: 'settings-preferences',
        label: 'Preferences',
        icon: Sliders,
        path: '/settings/preferences',
      },
    ],
  },
];
