'use client';

import { DollarSign } from 'lucide-react';
import { KPICard } from './KPICard';

interface SalesKPIProps {
  todaySales?: number;
  yesterdaySales?: number;
  isLoading?: boolean;
}

function formatLKR(amount: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function SalesKPI({ todaySales = 0, yesterdaySales = 0, isLoading }: SalesKPIProps) {
  const trendValue =
    yesterdaySales > 0 ? ((todaySales - yesterdaySales) / yesterdaySales) * 100 : 0;

  const direction = trendValue > 0 ? 'up' : trendValue < 0 ? 'down' : 'neutral';

  return (
    <KPICard
      title="Today's Sales"
      value={formatLKR(todaySales)}
      icon={DollarSign}
      trend={{
        value: trendValue,
        direction,
        label: 'vs yesterday',
      }}
      href="/reports/sales"
      variant="success"
      isLoading={isLoading}
    />
  );
}
