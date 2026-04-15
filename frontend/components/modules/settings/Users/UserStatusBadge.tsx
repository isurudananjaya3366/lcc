'use client';

import { Badge } from '@/components/ui/badge';
import { CheckCircle, Clock, Ban } from 'lucide-react';
import { cn } from '@/lib/utils';

type UserStatus = 'ACTIVE' | 'PENDING' | 'DISABLED';

const statusConfig: Record<
  UserStatus,
  { label: string; className: string; icon: React.ElementType }
> = {
  ACTIVE: {
    label: 'Active',
    className: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-100',
    icon: CheckCircle,
  },
  PENDING: {
    label: 'Pending',
    className: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-100',
    icon: Clock,
  },
  DISABLED: {
    label: 'Disabled',
    className: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-100',
    icon: Ban,
  },
};

interface UserStatusBadgeProps {
  status: UserStatus;
}

export function UserStatusBadge({ status }: UserStatusBadgeProps) {
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <Badge variant="outline" className={cn('gap-1 border-transparent', config.className)}>
      <Icon className="h-3 w-3" />
      {config.label}
    </Badge>
  );
}
