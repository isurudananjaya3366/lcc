'use client';

import Link from 'next/link';
import { Plus, Truck } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { StockTransfer } from '@/types/inventory';

interface TransfersHeaderProps {
  count: number;
  transfers: StockTransfer[];
}

export function TransfersHeader({ count, transfers }: TransfersHeaderProps) {
  const pending = transfers.filter((t) => t.status === 'PENDING').length;
  const completed = transfers.filter((t) => t.status === 'COMPLETED').length;

  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div className="flex items-center gap-2">
          <Truck className="h-6 w-6 text-gray-600 dark:text-gray-400" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Stock Transfers</h1>
          {count > 0 && (
            <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-400">
              {count}
            </span>
          )}
        </div>
        {count > 0 && (
          <div className="mt-1 flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
            <span className="text-yellow-600 dark:text-yellow-400">{pending} pending</span>
            <span className="text-green-600 dark:text-green-400">{completed} completed</span>
          </div>
        )}
      </div>
      <Button asChild>
        <Link href="/inventory/transfers/new">
          <Plus className="mr-2 h-4 w-4" />
          New Transfer
        </Link>
      </Button>
    </div>
  );
}
