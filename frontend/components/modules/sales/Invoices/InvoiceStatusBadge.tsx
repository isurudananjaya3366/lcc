'use client';

import { FileText, Send, CheckCircle, AlertCircle, AlertTriangle, XCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import type { InvoiceStatus } from '@/services/api/invoiceService';

interface InvoiceStatusBadgeProps {
  status: InvoiceStatus | string;
  size?: 'sm' | 'md' | 'lg';
}

const statusConfig: Record<string, { label: string; icon: React.ElementType; className: string }> =
  {
    draft: {
      label: 'Draft',
      icon: FileText,
      className: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300',
    },
    sent: {
      label: 'Sent',
      icon: Send,
      className: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
    },
    paid: {
      label: 'Paid',
      icon: CheckCircle,
      className: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
    },
    partially_paid: {
      label: 'Partial',
      icon: AlertCircle,
      className: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
    },
    overdue: {
      label: 'Overdue',
      icon: AlertTriangle,
      className: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
    },
    void: {
      label: 'Void',
      icon: XCircle,
      className: 'bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400',
    },
    cancelled: {
      label: 'Cancelled',
      icon: XCircle,
      className: 'bg-red-200 text-red-700 dark:bg-red-900 dark:text-red-400',
    },
  };

const sizeClasses = {
  sm: 'text-xs px-2 py-0.5',
  md: 'text-xs px-2.5 py-1',
  lg: 'text-sm px-3 py-1',
};

const iconSizes = { sm: 'h-3 w-3', md: 'h-3.5 w-3.5', lg: 'h-4 w-4' };

export function InvoiceStatusBadge({ status, size = 'md' }: InvoiceStatusBadgeProps) {
  const config = statusConfig[status] ?? statusConfig['draft']!;
  const Icon = config.icon;

  return (
    <Badge
      variant="secondary"
      className={`${config.className} ${sizeClasses[size]} inline-flex items-center gap-1`}
      aria-label={`Status: ${config.label}`}
      title={config.label}
    >
      <Icon className={iconSizes[size]} />
      {config.label}
    </Badge>
  );
}
