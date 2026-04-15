'use client';

import { FileText, CheckCircle, Clock, Truck, Package, XCircle, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { OrderStatus } from '@/types/sales';

interface OrderStatusBannerProps {
  status: OrderStatus;
  message?: string;
  onActionClick?: () => void;
  onDismiss?: () => void;
}

const bannerConfig: Record<
  string,
  { bg: string; icon: React.ElementType; defaultMessage: string; actionLabel?: string }
> = {
  DRAFT: {
    bg: 'bg-gray-50 border-gray-200 text-gray-800 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200',
    icon: FileText,
    defaultMessage: 'This order is a draft and has not been confirmed yet.',
    actionLabel: 'Confirm Order',
  },
  PENDING: {
    bg: 'bg-yellow-50 border-yellow-200 text-yellow-800 dark:bg-yellow-900/30 dark:border-yellow-700 dark:text-yellow-200',
    icon: Clock,
    defaultMessage: 'This order is pending confirmation.',
    actionLabel: 'Confirm Order',
  },
  CONFIRMED: {
    bg: 'bg-blue-50 border-blue-200 text-blue-800 dark:bg-blue-900/30 dark:border-blue-700 dark:text-blue-200',
    icon: CheckCircle,
    defaultMessage: 'Order has been confirmed and is ready for processing.',
    actionLabel: 'Start Processing',
  },
  PROCESSING: {
    bg: 'bg-indigo-50 border-indigo-200 text-indigo-800 dark:bg-indigo-900/30 dark:border-indigo-700 dark:text-indigo-200',
    icon: Clock,
    defaultMessage: 'Order is currently being processed.',
    actionLabel: 'Mark as Shipped',
  },
  SHIPPED: {
    bg: 'bg-purple-50 border-purple-200 text-purple-800 dark:bg-purple-900/30 dark:border-purple-700 dark:text-purple-200',
    icon: Truck,
    defaultMessage: 'Order has been shipped and is on its way.',
    actionLabel: 'Mark Delivered',
  },
  DELIVERED: {
    bg: 'bg-green-50 border-green-200 text-green-800 dark:bg-green-900/30 dark:border-green-700 dark:text-green-200',
    icon: Package,
    defaultMessage: 'Order has been delivered successfully.',
  },
  COMPLETED: {
    bg: 'bg-emerald-50 border-emerald-200 text-emerald-800 dark:bg-emerald-900/30 dark:border-emerald-700 dark:text-emerald-200',
    icon: CheckCircle,
    defaultMessage: 'Order is complete.',
  },
  CANCELLED: {
    bg: 'bg-red-50 border-red-200 text-red-800 dark:bg-red-900/30 dark:border-red-700 dark:text-red-200',
    icon: XCircle,
    defaultMessage: 'This order has been cancelled.',
  },
  REFUNDED: {
    bg: 'bg-orange-50 border-orange-200 text-orange-800 dark:bg-orange-900/30 dark:border-orange-700 dark:text-orange-200',
    icon: XCircle,
    defaultMessage: 'This order has been refunded.',
  },
};

export function OrderStatusBanner({
  status,
  message,
  onActionClick,
  onDismiss,
}: OrderStatusBannerProps) {
  const config = bannerConfig[status] ?? bannerConfig['DRAFT']!;
  const Icon = config.icon;

  return (
    <div
      className={cn('flex items-center gap-3 rounded-lg border p-4', config.bg)}
      role="alert"
      aria-live="polite"
    >
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-current/10">
        <Icon className="h-5 w-5" />
      </div>
      <p className="flex-1 text-sm font-medium">{message || config.defaultMessage}</p>
      {config.actionLabel && onActionClick && (
        <Button size="sm" variant="outline" onClick={onActionClick} className="shrink-0">
          {config.actionLabel}
        </Button>
      )}
      {onDismiss && (
        <button onClick={onDismiss} className="shrink-0 rounded p-1 hover:bg-black/5">
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
