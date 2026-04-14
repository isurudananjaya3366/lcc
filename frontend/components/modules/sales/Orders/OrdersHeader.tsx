'use client';

import Link from 'next/link';
import { ShoppingCart, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface OrdersHeaderProps {
  orderCount?: number;
}

export function OrdersHeader({ orderCount }: OrdersHeaderProps) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-3">
        <ShoppingCart className="h-6 w-6 text-blue-600 dark:text-blue-400" />
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            All Orders
            {orderCount !== undefined && (
              <span className="ml-2 text-sm font-normal text-gray-500">({orderCount})</span>
            )}
          </h2>
        </div>
      </div>
      <Link href="/orders/new">
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Order
        </Button>
      </Link>
    </div>
  );
}
