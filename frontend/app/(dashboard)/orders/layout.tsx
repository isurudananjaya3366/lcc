'use client';

import type { ReactNode } from 'react';
import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';
import { cn } from '@/lib/utils';
import { ShoppingCart, Clock, Cog, Truck, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';

const tabs = [
  { label: 'All Orders', href: '/orders', status: undefined, icon: ShoppingCart },
  { label: 'Pending', href: '/orders?status=pending', status: 'pending', icon: Clock },
  { label: 'Processing', href: '/orders?status=processing', status: 'processing', icon: Cog },
  { label: 'Shipped', href: '/orders?status=shipped', status: 'shipped', icon: Truck },
] as const;

export default function OrdersLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const currentStatus = searchParams.get('status');

  // Only show tabs on the orders list page
  const isListPage = pathname === '/orders';

  const isActive = (tab: (typeof tabs)[number]) => {
    if (!isListPage) return false;
    if (!tab.status) return !currentStatus;
    return currentStatus === tab.status;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-gray-100 sm:text-3xl">
            Orders
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Manage and track all customer orders
          </p>
        </div>
        <Link href="/orders/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Order
          </Button>
        </Link>
      </div>

      {/* Tab Navigation — only on list page */}
      {isListPage && (
        <nav
          className="border-b border-gray-200 dark:border-gray-700"
          aria-label="Order status tabs"
        >
          <div className="-mb-px flex space-x-8 overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <Link
                  key={tab.label}
                  href={tab.href}
                  className={cn(
                    'flex items-center gap-2 whitespace-nowrap border-b-2 px-1 py-3 text-sm font-medium transition-colors',
                    isActive(tab)
                      ? 'border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:border-gray-600 dark:hover:text-gray-300'
                  )}
                  aria-current={isActive(tab) ? 'page' : undefined}
                >
                  <Icon className="h-4 w-4" />
                  {tab.label}
                </Link>
              );
            })}
          </div>
        </nav>
      )}

      {/* Content */}
      <div>{children}</div>
    </div>
  );
}
