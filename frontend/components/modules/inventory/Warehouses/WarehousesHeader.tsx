'use client';

import Link from 'next/link';
import { Plus, Warehouse, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface WarehousesHeaderProps {
  count: number;
  activeCount: number;
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

export function WarehousesHeader({
  count,
  activeCount,
  searchQuery,
  onSearchChange,
}: WarehousesHeaderProps) {
  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Warehouse className="h-6 w-6 text-gray-600 dark:text-gray-400" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Warehouses</h1>
            {count > 0 && (
              <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                {count}
              </span>
            )}
          </div>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {activeCount} active warehouse{activeCount !== 1 ? 's' : ''}
          </p>
        </div>
        <Button asChild>
          <Link href="/inventory/warehouses/new">
            <Plus className="mr-2 h-4 w-4" />
            New Warehouse
          </Link>
        </Button>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <Input
          placeholder="Search warehouses..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-9"
        />
      </div>
    </div>
  );
}
