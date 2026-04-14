'use client';

import { CheckCircle, AlertTriangle, XCircle, TrendingUp } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StockLevelCellProps {
  quantity: number;
  reorderPoint?: number;
  maxLevel?: number;
}

type StockStatus = 'in-stock' | 'low-stock' | 'out-of-stock' | 'overstocked';

function getStockStatus(quantity: number, reorderPoint?: number, maxLevel?: number): StockStatus {
  if (quantity <= 0) return 'out-of-stock';
  if (maxLevel && quantity > maxLevel) return 'overstocked';
  if (reorderPoint && quantity < reorderPoint) return 'low-stock';
  return 'in-stock';
}

const statusConfig: Record<
  StockStatus,
  {
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    badgeClass: string;
  }
> = {
  'in-stock': {
    label: 'In Stock',
    icon: CheckCircle,
    badgeClass: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  },
  'low-stock': {
    label: 'Low Stock',
    icon: AlertTriangle,
    badgeClass: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
  },
  'out-of-stock': {
    label: 'Out of Stock',
    icon: XCircle,
    badgeClass: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  },
  overstocked: {
    label: 'Overstocked',
    icon: TrendingUp,
    badgeClass: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  },
};

export function StockLevelCell({ quantity, reorderPoint, maxLevel }: StockLevelCellProps) {
  const status = getStockStatus(quantity, reorderPoint, maxLevel);
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium',
        config.badgeClass
      )}
      title={`Available: ${quantity}${reorderPoint ? ` | Reorder: ${reorderPoint}` : ''}`}
    >
      <Icon className="h-3 w-3" />
      {config.label}
    </span>
  );
}
