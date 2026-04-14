'use client';

import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { ProductStatus } from '@/types/product';

interface StatusBadgeCellProps {
  status: ProductStatus;
}

const statusConfig: Record<ProductStatus, { label: string; className: string }> = {
  [ProductStatus.ACTIVE]: {
    label: 'Active',
    className:
      'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800',
  },
  [ProductStatus.DRAFT]: {
    label: 'Draft',
    className:
      'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800',
  },
  [ProductStatus.DISCONTINUED]: {
    label: 'Discontinued',
    className:
      'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-700',
  },
  [ProductStatus.OUT_OF_STOCK]: {
    label: 'Out of Stock',
    className:
      'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800',
  },
};

export function StatusBadgeCell({ status }: StatusBadgeCellProps) {
  const config = statusConfig[status] ?? statusConfig[ProductStatus.DRAFT];

  return (
    <Badge variant="outline" className={cn(config.className)}>
      {config.label}
    </Badge>
  );
}
