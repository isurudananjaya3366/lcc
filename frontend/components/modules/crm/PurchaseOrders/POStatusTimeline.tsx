'use client';

import { Badge } from '@/components/ui/badge';
import type { PurchaseOrder } from '@/types/vendor';

type StatusVariant =
  | 'default'
  | 'secondary'
  | 'destructive'
  | 'outline'
  | 'pending'
  | 'confirmed'
  | 'processing'
  | 'shipped'
  | 'delivered'
  | 'cancelled'
  | 'failed';

const statusSteps: { key: PurchaseOrder['status']; label: string; variant: StatusVariant }[] = [
  { key: 'DRAFT', label: 'Draft', variant: 'secondary' },
  { key: 'SENT', label: 'Sent', variant: 'pending' },
  { key: 'ACKNOWLEDGED', label: 'Acknowledged', variant: 'confirmed' },
  { key: 'SHIPPED', label: 'Shipped', variant: 'shipped' },
  { key: 'RECEIVED', label: 'Received', variant: 'delivered' },
];

interface POStatusTimelineProps {
  status: PurchaseOrder['status'];
}

export function POStatusTimeline({ status }: POStatusTimelineProps) {
  if (status === 'CANCELLED') {
    return (
      <div className="flex items-center gap-2">
        <Badge variant="cancelled">Cancelled</Badge>
      </div>
    );
  }

  const currentIndex = statusSteps.findIndex((s) => s.key === status);

  return (
    <div className="flex items-center gap-1 flex-wrap">
      {statusSteps.map((step, idx) => {
        const isActive = idx <= currentIndex;
        return (
          <div key={step.key} className="flex items-center gap-1">
            <div className={`h-2 w-2 rounded-full ${isActive ? 'bg-primary' : 'bg-muted'}`} />
            <span className={`text-xs ${isActive ? 'font-medium' : 'text-muted-foreground'}`}>
              {step.label}
            </span>
            {idx < statusSteps.length - 1 && (
              <div className={`h-px w-4 ${idx < currentIndex ? 'bg-primary' : 'bg-muted'}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
