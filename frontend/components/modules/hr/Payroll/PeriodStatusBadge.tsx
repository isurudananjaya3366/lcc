'use client';

import { Badge } from '@/components/ui/badge';

type PayrollStatus = 'DRAFT' | 'PROCESSING' | 'PROCESSED' | 'PAID';

const statusConfig: Record<
  PayrollStatus,
  { label: string; variant: 'secondary' | 'default' | 'outline' | 'destructive' }
> = {
  DRAFT: { label: 'Draft', variant: 'secondary' },
  PROCESSING: { label: 'Processing', variant: 'outline' },
  PROCESSED: { label: 'Processed', variant: 'default' },
  PAID: { label: 'Paid', variant: 'default' },
};

interface PeriodStatusBadgeProps {
  status: string;
}

export function PeriodStatusBadge({ status }: PeriodStatusBadgeProps) {
  const config = statusConfig[status as PayrollStatus] ?? {
    label: status,
    variant: 'secondary' as const,
  };

  return <Badge variant={config.variant}>{config.label}</Badge>;
}
