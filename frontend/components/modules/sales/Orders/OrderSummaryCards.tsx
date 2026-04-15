'use client';

import { ShoppingCart, Clock, Truck, DollarSign } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { Order } from '@/types/sales';

interface OrderSummaryCardsProps {
  orders: Order[];
  isLoading: boolean;
}

export function OrderSummaryCards({ orders, isLoading }: OrderSummaryCardsProps) {
  const totalOrders = orders.length;
  const pendingOrders = orders.filter(
    (o) => o.orderStatus === 'PENDING' || o.orderStatus === 'DRAFT'
  ).length;
  const shippedToday = orders.filter((o) => {
    if (o.orderStatus !== 'SHIPPED') return false;
    const today = new Date().toISOString().split('T')[0] ?? '';
    return o.updatedAt?.startsWith(today) ?? false;
  }).length;
  const totalRevenue = orders.reduce((sum, o) => sum + (o.total ?? 0), 0);

  const cards = [
    {
      title: 'Total Orders',
      value: isLoading ? '—' : totalOrders.toString(),
      description: 'All orders',
      icon: ShoppingCart,
      iconColor: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
    },
    {
      title: 'Pending Orders',
      value: isLoading ? '—' : pendingOrders.toString(),
      description: 'Awaiting processing',
      icon: Clock,
      iconColor: 'text-yellow-600 dark:text-yellow-400',
      bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
    },
    {
      title: 'Shipped Today',
      value: isLoading ? '—' : shippedToday.toString(),
      description: 'Orders dispatched',
      icon: Truck,
      iconColor: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-green-50 dark:bg-green-900/20',
    },
    {
      title: 'Total Revenue',
      value: isLoading
        ? '—'
        : `₨ ${totalRevenue.toLocaleString(undefined, { minimumFractionDigits: 2 })}`,
      description: 'Order value',
      icon: DollarSign,
      iconColor: 'text-emerald-600 dark:text-emerald-400',
      bgColor: 'bg-emerald-50 dark:bg-emerald-900/20',
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <Card key={card.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-500 dark:text-gray-400">
                {card.title}
              </CardTitle>
              <div className={`rounded-md p-2 ${card.bgColor}`}>
                <Icon className={`h-4 w-4 ${card.iconColor}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {card.value}
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400">{card.description}</p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
