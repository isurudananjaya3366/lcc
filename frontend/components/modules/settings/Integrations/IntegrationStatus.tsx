'use client';

import { Badge } from '@/components/ui/badge';
import { CheckCircle, Circle, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

type IntegrationStatusType = 'CONNECTED' | 'DISCONNECTED';

const statusConfig: Record<
  IntegrationStatusType,
  { label: string; className: string; icon: React.ElementType }
> = {
  CONNECTED: {
    label: 'Connected',
    className: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-100',
    icon: CheckCircle,
  },
  DISCONNECTED: {
    label: 'Disconnected',
    className: 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400',
    icon: Circle,
  },
};

interface IntegrationStatusProps {
  status: IntegrationStatusType;
}

export function IntegrationStatus({ status }: IntegrationStatusProps) {
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <Badge variant="outline" className={cn('gap-1 border-transparent', config.className)}>
      <Icon className="h-3 w-3" />
      {config.label}
    </Badge>
  );
}
