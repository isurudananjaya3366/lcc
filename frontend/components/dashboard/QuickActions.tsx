'use client';

import Link from 'next/link';
import { ShoppingCart, Package, FileText, UserPlus } from 'lucide-react';
import { cn } from '@/lib/cn';

interface QuickActionItem {
  title: string;
  description: string;
  href: string;
  icon: React.ElementType;
  color: string;
}

const quickActions: QuickActionItem[] = [
  {
    title: 'New Sale',
    description: 'Create a new sales order',
    href: '/sales/orders/new',
    icon: ShoppingCart,
    color: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
  },
  {
    title: 'Add Product',
    description: 'Add a new inventory item',
    href: '/inventory/products/new',
    icon: Package,
    color: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
  },
  {
    title: 'Create Invoice',
    description: 'Generate a new invoice',
    href: '/accounting/invoices/new',
    icon: FileText,
    color: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
  },
  {
    title: 'Add Customer',
    description: 'Register a new customer',
    href: '/sales/customers/new',
    icon: UserPlus,
    color: 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400',
  },
];

export function DashboardQuickActions() {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {quickActions.map((action) => {
        const Icon = action.icon;
        return (
          <Link
            key={action.title}
            href={action.href}
            className={cn(
              'flex min-h-[44px] items-center gap-3 rounded-xl border border-gray-200 bg-white p-4 shadow-sm transition-all',
              'hover:border-gray-300 hover:shadow-md',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
              'dark:border-gray-700 dark:bg-gray-800 dark:hover:border-gray-600'
            )}
          >
            <div
              className={cn(
                'flex h-10 w-10 shrink-0 items-center justify-center rounded-lg',
                action.color
              )}
            >
              <Icon className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                {action.title}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">{action.description}</p>
            </div>
          </Link>
        );
      })}
    </div>
  );
}
