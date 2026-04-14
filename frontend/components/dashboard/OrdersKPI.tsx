'use client';

import { ShoppingBag } from 'lucide-react';
import { KPICard } from './KPICard';

interface OrdersKPIProps {
  todayOrders?: number;
  yesterdayOrders?: number;
  isLoading?: boolean;
}

export function OrdersKPI({ todayOrders = 0, yesterdayOrders = 0, isLoading }: OrdersKPIProps) {
  const trendValue =
    yesterdayOrders > 0 ? ((todayOrders - yesterdayOrders) / yesterdayOrders) * 100 : 0;

  const direction = trendValue > 0 ? 'up' : trendValue < 0 ? 'down' : 'neutral';

  return (
    <KPICard
      title="Today's Orders"
      value={todayOrders.toLocaleString()}
      icon={ShoppingBag}
      trend={{
        value: trendValue,
        direction,
        label: 'vs yesterday',
      }}
      href="/sales/orders"
      isLoading={isLoading}
    />
  );
}
