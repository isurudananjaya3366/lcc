'use client';

import type { Warehouse } from '@/types/inventory';
import { WarehouseCard } from './WarehouseCard';

interface WarehouseCardsProps {
  warehouses: Warehouse[];
  isLoading?: boolean;
}

export function WarehouseCards({ warehouses, isLoading }: WarehouseCardsProps) {
  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className="h-52 animate-pulse rounded-lg border border-gray-200 bg-gray-100 dark:border-gray-700 dark:bg-gray-800"
          />
        ))}
      </div>
    );
  }

  if (warehouses.length === 0) {
    return (
      <div className="rounded-md border border-dashed border-gray-300 p-12 text-center dark:border-gray-700">
        <p className="text-sm text-gray-500 dark:text-gray-400">No warehouses found.</p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {warehouses.map((warehouse) => (
        <WarehouseCard key={warehouse.id} warehouse={warehouse} />
      ))}
    </div>
  );
}
