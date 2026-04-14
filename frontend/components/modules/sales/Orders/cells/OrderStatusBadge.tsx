'use client';

import { Badge } from '@/components/ui/badge';
import {
  FileText,
  CheckCircle,
  Clock,
  Truck,
  Package,
  XCircle,
  Star,
  RotateCcw,
  ShieldCheck,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import type { OrderStatus } from '@/types/sales';

interface OrderStatusBadgeProps {
  status: OrderStatus;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

const statusConfig: Record<
  OrderStatus,
  { label: string; color: string; icon: React.ElementType; description: string }
> = {
  DRAFT: {
    label: 'Draft',
    color: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    icon: FileText,
    description: 'Order not yet confirmed',
  },
  PENDING: {
    label: 'Pending',
    color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
    icon: Clock,
    description: 'Awaiting confirmation',
  },
  CONFIRMED: {
    label: 'Confirmed',
    color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
    icon: CheckCircle,
    description: 'Order confirmed by customer',
  },
  PROCESSING: {
    label: 'Processing',
    color: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-300',
    icon: Clock,
    description: 'Order being prepared',
  },
  SHIPPED: {
    label: 'Shipped',
    color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
    icon: Truck,
    description: 'Order shipped to customer',
  },
  DELIVERED: {
    label: 'Delivered',
    color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
    icon: Package,
    description: 'Order delivered successfully',
  },
  COMPLETED: {
    label: 'Completed',
    color: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-300',
    icon: Star,
    description: 'Order completed',
  },
  CANCELLED: {
    label: 'Cancelled',
    color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
    icon: XCircle,
    description: 'Order cancelled',
  },
  REFUNDED: {
    label: 'Refunded',
    color: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
    icon: RotateCcw,
    description: 'Order refunded',
  },
};

const sizeClasses = {
  sm: 'text-xs px-2 py-0.5',
  md: 'text-xs px-2.5 py-0.5',
  lg: 'text-sm px-3 py-1',
};

const iconSizes = { sm: 12, md: 14, lg: 16 };

export function OrderStatusBadge({ status, className, size = 'md' }: OrderStatusBadgeProps) {
  const config = statusConfig[status] ?? {
    label: status,
    color: 'bg-gray-100 text-gray-800',
    icon: ShieldCheck,
    description: 'Unknown status',
  };

  const Icon = config.icon;

  return (
    <Badge
      variant="secondary"
      className={cn(config.color, sizeClasses[size], 'inline-flex items-center gap-1', className)}
      title={config.description}
      aria-label={`Status: ${config.label}`}
    >
      <Icon size={iconSizes[size]} />
      {config.label}
    </Badge>
  );
}

export type { OrderStatusBadgeProps };
