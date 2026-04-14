'use client';

import type { ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Package, TrendingUp, Edit, ArrowRightLeft, Building2 } from 'lucide-react';

const tabs = [
  { label: 'Stock Levels', href: '/inventory', icon: Package },
  { label: 'Movements', href: '/inventory/movements', icon: TrendingUp },
  { label: 'Adjustments', href: '/inventory/adjustments', icon: Edit },
  { label: 'Transfers', href: '/inventory/transfers', icon: ArrowRightLeft },
  { label: 'Warehouses', href: '/inventory/warehouses', icon: Building2 },
] as const;

export default function InventoryLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === '/inventory') {
      return (
        pathname === '/inventory' ||
        (pathname.startsWith('/inventory') &&
          !pathname.startsWith('/inventory/movements') &&
          !pathname.startsWith('/inventory/adjustments') &&
          !pathname.startsWith('/inventory/transfers') &&
          !pathname.startsWith('/inventory/warehouses'))
      );
    }
    return pathname.startsWith(href);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-gray-100 sm:text-3xl">
            Inventory Management
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Manage stock levels, movements, adjustments, and warehouses
          </p>
        </div>
      </div>

      {/* Tab Navigation */}
      <nav
        className="border-b border-gray-200 dark:border-gray-700"
        aria-label="Inventory sections"
      >
        <div className="-mb-px flex space-x-8 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={cn(
                  'flex items-center gap-2 whitespace-nowrap border-b-2 px-1 py-3 text-sm font-medium transition-colors',
                  isActive(tab.href)
                    ? 'border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:border-gray-600 dark:hover:text-gray-300'
                )}
                aria-current={isActive(tab.href) ? 'page' : undefined}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Content */}
      <div>{children}</div>
    </div>
  );
}
