'use client';

import { Clock, Truck, CheckCircle2, XCircle, type LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { StockMovementStatus } from '@/types/inventory';

interface TransferStatusBadgeProps {
  status: StockMovementStatus;
  size?: 'sm' | 'md' | 'lg';
}

const statusConfig: Record<
  StockMovementStatus,
  { label: string; icon: LucideIcon; className: string }
> = {
  PENDING: {
    label: 'Pending',
    icon: Clock,
    className: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
  },
  COMPLETED: {
    label: 'Received',
    icon: CheckCircle2,
    className: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  },
  CANCELLED: {
    label: 'Cancelled',
    icon: XCircle,
    className: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400',
  },
};

const sizeClasses = {
  sm: 'px-1.5 py-0.5 text-xs',
  md: 'px-2 py-0.5 text-xs',
  lg: 'px-2.5 py-1 text-sm',
};

const iconSizes = {
  sm: 'h-3 w-3',
  md: 'h-3.5 w-3.5',
  lg: 'h-4 w-4',
};

export function TransferStatusBadge({ status, size = 'md' }: TransferStatusBadgeProps) {
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full font-medium',
        config.className,
        sizeClasses[size]
      )}
    >
      <Icon className={iconSizes[size]} />
      {config.label}
    </span>
  );
}
