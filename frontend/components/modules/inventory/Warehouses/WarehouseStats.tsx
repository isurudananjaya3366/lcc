'use client';

import { Package, BarChart3 } from 'lucide-react';
import type { Warehouse } from '@/types/inventory';
import { cn } from '@/lib/utils';

interface WarehouseStatsProps {
  warehouse: Warehouse;
}

export function WarehouseStats({ warehouse }: WarehouseStatsProps) {
  const utilization = warehouse.currentUtilization ?? 0;
  const capacity = warehouse.capacity ?? 0;
  const utilizationPct = capacity > 0 ? Math.round((utilization / capacity) * 100) : 0;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
          <Package className="h-3.5 w-3.5" />
          <span>Items</span>
        </div>
        <span className="font-medium text-gray-900 dark:text-gray-100">{utilization}</span>
      </div>

      {capacity > 0 && (
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>Capacity</span>
            <span>{utilizationPct}%</span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
            <div
              className={cn(
                'h-full rounded-full transition-all',
                utilizationPct <= 50
                  ? 'bg-green-500'
                  : utilizationPct <= 80
                    ? 'bg-yellow-500'
                    : utilizationPct <= 95
                      ? 'bg-orange-500'
                      : 'bg-red-500'
              )}
              style={{ width: `${Math.min(utilizationPct, 100)}%` }}
            />
          </div>
        </div>
      )}

      <div className="flex items-center gap-1.5 text-xs">
        <span
          className={cn(
            'inline-flex items-center gap-1 rounded-full px-1.5 py-0.5 font-medium',
            warehouse.isActive
              ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
              : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
          )}
        >
          {warehouse.isActive ? 'Active' : 'Inactive'}
        </span>
      </div>
    </div>
  );
}
