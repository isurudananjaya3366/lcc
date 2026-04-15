'use client';

import { Card, CardContent } from '@/components/ui/card';
import { DollarSign, Clock, CheckCircle } from 'lucide-react';
import type { Payroll } from '@/types/hr';

interface PayrollSummaryCardsProps {
  payrolls: Payroll[];
}

function formatLKR(amount: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 2,
  }).format(amount);
}

export function PayrollSummaryCards({ payrolls }: PayrollSummaryCardsProps) {
  const totalPayroll = payrolls.reduce((sum, p) => sum + p.totalNet, 0);
  const pending = payrolls.filter((p) => p.status === 'DRAFT' || p.status === 'PROCESSING').length;
  const processed = payrolls.filter((p) => p.status === 'PROCESSED' || p.status === 'PAID').length;

  const cards = [
    {
      title: 'Total Payroll',
      value: formatLKR(totalPayroll),
      icon: DollarSign,
      color: 'text-green-600',
    },
    {
      title: 'Pending',
      value: String(pending),
      icon: Clock,
      color: 'text-yellow-600',
    },
    {
      title: 'Processed',
      value: String(processed),
      icon: CheckCircle,
      color: 'text-blue-600',
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardContent className="flex items-center gap-4 p-6">
            <div className={`rounded-lg bg-muted p-3 ${card.color}`}>
              <card.icon className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{card.title}</p>
              <p className="text-xl font-bold">{card.value}</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
