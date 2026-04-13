import * as React from 'react';
import { cn } from '@/lib/utils';

// ================================================================
// StatusIndicator — Color-coded status badge with optional dot
// ================================================================

export type StatusType =
  | 'active'
  | 'inactive'
  | 'pending'
  | 'processing'
  | 'completed'
  | 'cancelled'
  | 'failed'
  | 'paid'
  | 'unpaid'
  | 'partial'
  | 'shipped'
  | 'delivered';

const statusConfig: Record<StatusType, { label: string; bg: string; text: string; dot: string }> = {
  active:     { label: 'Active',         bg: 'bg-green-100 dark:bg-green-900/30',  text: 'text-green-700 dark:text-green-400',  dot: 'bg-green-500' },
  inactive:   { label: 'Inactive',       bg: 'bg-gray-100 dark:bg-gray-800/50',    text: 'text-gray-600 dark:text-gray-400',    dot: 'bg-gray-400' },
  pending:    { label: 'Pending',        bg: 'bg-yellow-100 dark:bg-yellow-900/30', text: 'text-yellow-700 dark:text-yellow-400', dot: 'bg-yellow-500' },
  processing: { label: 'Processing',    bg: 'bg-blue-100 dark:bg-blue-900/30',    text: 'text-blue-700 dark:text-blue-400',    dot: 'bg-blue-500' },
  completed:  { label: 'Completed',     bg: 'bg-green-100 dark:bg-green-900/30',  text: 'text-green-700 dark:text-green-400',  dot: 'bg-green-500' },
  cancelled:  { label: 'Cancelled',     bg: 'bg-red-100 dark:bg-red-900/30',      text: 'text-red-700 dark:text-red-400',      dot: 'bg-red-500' },
  failed:     { label: 'Failed',        bg: 'bg-red-100 dark:bg-red-900/30',      text: 'text-red-700 dark:text-red-400',      dot: 'bg-red-500' },
  paid:       { label: 'Paid',          bg: 'bg-green-100 dark:bg-green-900/30',  text: 'text-green-700 dark:text-green-400',  dot: 'bg-green-500' },
  unpaid:     { label: 'Unpaid',        bg: 'bg-red-100 dark:bg-red-900/30',      text: 'text-red-700 dark:text-red-400',      dot: 'bg-red-500' },
  partial:    { label: 'Partially Paid', bg: 'bg-orange-100 dark:bg-orange-900/30', text: 'text-orange-700 dark:text-orange-400', dot: 'bg-orange-500' },
  shipped:    { label: 'Shipped',       bg: 'bg-blue-100 dark:bg-blue-900/30',    text: 'text-blue-700 dark:text-blue-400',    dot: 'bg-blue-500' },
  delivered:  { label: 'Delivered',     bg: 'bg-green-100 dark:bg-green-900/30',  text: 'text-green-700 dark:text-green-400',  dot: 'bg-green-500' },
};

const sizeClasses = {
  sm: 'text-xs px-2 py-0.5',
  md: 'text-sm px-2.5 py-1',
  lg: 'text-base px-3 py-1.5',
} as const;

const dotSizeClasses = {
  sm: 'size-1.5',
  md: 'size-2',
  lg: 'size-2.5',
} as const;

export interface StatusIndicatorProps {
  status: StatusType;
  label?: string;
  showDot?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function StatusIndicator({
  status,
  label,
  showDot = false,
  size = 'md',
  className,
}: StatusIndicatorProps) {
  const config = statusConfig[status];

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full font-medium whitespace-nowrap',
        config.bg,
        config.text,
        sizeClasses[size],
        className,
      )}
    >
      {showDot && (
        <span
          className={cn(
            'shrink-0 rounded-full',
            config.dot,
            dotSizeClasses[size],
            (status === 'active' || status === 'processing') && 'animate-pulse',
          )}
          aria-hidden="true"
        />
      )}
      {label ?? config.label}
    </span>
  );
}
