'use client';

import { Badge } from '@/components/ui/badge';
import type { LeaveStatus } from '@/types/hr';

interface LeaveStatusBadgeProps {
  status: LeaveStatus;
}

const statusConfig: Record<
  LeaveStatus,
  { variant: 'default' | 'secondary' | 'destructive' | 'outline'; label: string }
> = {
  PENDING: { variant: 'secondary', label: 'Pending' },
  APPROVED: { variant: 'default', label: 'Approved' },
  REJECTED: { variant: 'destructive', label: 'Rejected' },
  CANCELLED: { variant: 'outline', label: 'Cancelled' },
};

export function LeaveStatusBadge({ status }: LeaveStatusBadgeProps) {
  const config = statusConfig[status] ?? { variant: 'outline' as const, label: status };

  return <Badge variant={config.variant}>{config.label}</Badge>;
}
