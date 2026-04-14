'use client';

import { FileText, Send, CheckCircle, XCircle, Clock, ArrowRightLeft } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import type { QuoteStatus } from '@/types/quotes';

interface QuoteStatusBadgeProps {
  status: QuoteStatus;
  size?: 'sm' | 'md' | 'lg';
}

const statusConfig: Record<
  QuoteStatus,
  { label: string; icon: React.ElementType; className: string }
> = {
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
  accepted: {
    label: 'Accepted',
    icon: CheckCircle,
    className: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
  },
  rejected: {
    label: 'Rejected',
    icon: XCircle,
    className: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
  },
  expired: {
    label: 'Expired',
    icon: Clock,
    className: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
  },
  converted: {
    label: 'Converted',
    icon: ArrowRightLeft,
    className: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-300',
  },
};

const sizeClasses = {
  sm: 'text-xs px-2 py-0.5',
  md: 'text-xs px-2.5 py-1',
  lg: 'text-sm px-3 py-1',
};

const iconSizes = { sm: 'h-3 w-3', md: 'h-3.5 w-3.5', lg: 'h-4 w-4' };

export function QuoteStatusBadge({ status, size = 'md' }: QuoteStatusBadgeProps) {
  const config = statusConfig[status];
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
