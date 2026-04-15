'use client';

import { FileText, Clock, CheckCircle, XCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import type { PurchaseOrder } from '@/types/vendor';

interface POSummaryCardsProps {
  orders: PurchaseOrder[];
}

export function POSummaryCards({ orders }: POSummaryCardsProps) {
  const totalOrders = orders.length;
  const draftCount = orders.filter((o) => o.status === 'DRAFT').length;
  const pendingCount = orders.filter((o) =>
    ['SENT', 'ACKNOWLEDGED', 'SHIPPED'].includes(o.status)
  ).length;
  const completedCount = orders.filter((o) => o.status === 'RECEIVED').length;
  const totalValue = orders.reduce((sum, o) => sum + o.total, 0);

  const cards = [
    {
      label: 'Total Orders',
      value: totalOrders.toString(),
      icon: FileText,
      description: `₨ ${totalValue.toLocaleString('en-LK')} total value`,
    },
    {
      label: 'Draft',
      value: draftCount.toString(),
      icon: Clock,
      description: 'Awaiting submission',
    },
    {
      label: 'In Progress',
      value: pendingCount.toString(),
      icon: Clock,
      description: 'Sent / Acknowledged / Shipped',
    },
    {
      label: 'Received',
      value: completedCount.toString(),
      icon: CheckCircle,
      description: 'Successfully delivered',
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <Card key={card.label}>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <card.icon className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">{card.label}</span>
            </div>
            <p className="text-2xl font-bold mt-1">{card.value}</p>
            <p className="text-xs text-muted-foreground">{card.description}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
