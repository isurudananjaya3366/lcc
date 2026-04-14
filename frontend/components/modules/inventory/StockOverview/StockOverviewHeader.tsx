'use client';

import Link from 'next/link';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function StockOverviewHeader() {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Stock Levels</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Monitor stock across all warehouses
        </p>
      </div>
      <Link href="/inventory/adjustments/new">
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Adjustment
        </Button>
      </Link>
    </div>
  );
}
