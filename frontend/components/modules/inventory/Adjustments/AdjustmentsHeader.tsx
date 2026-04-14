'use client';

import Link from 'next/link';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface AdjustmentsHeaderProps {
  count: number;
}

export function AdjustmentsHeader({ count }: AdjustmentsHeaderProps) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-3">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
          Stock Adjustments
        </h2>
        <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-700 dark:bg-gray-800 dark:text-gray-300">
          {count.toLocaleString()}
        </span>
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
