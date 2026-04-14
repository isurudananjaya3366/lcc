'use client';

import { useMemo } from 'react';
import { Package, AlertTriangle, XCircle, DollarSign } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { StockLevel } from '@/types/inventory';

interface StockSummaryCardsProps {
  data: StockLevel[];
  isLoading?: boolean;
}

interface SummaryCard {
  label: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  iconColor: string;
  bgColor: string;
  description: string;
}

export function StockSummaryCards({ data, isLoading }: StockSummaryCardsProps) {
  const summary = useMemo(() => {
    const totalProducts = data.length;
    const lowStock = data.filter((s) => s.quantityAvailable > 0 && s.quantityAvailable < 10).length;
    const outOfStock = data.filter((s) => s.quantityAvailable <= 0).length;
    const totalValue = data.reduce((sum, s) => sum + s.quantityOnHand * 1, 0);

    return { totalProducts, lowStock, outOfStock, totalValue };
  }, [data]);

  // Severity-based colors for low stock card (Task 19)
  const lowStockSeverity = useMemo(() => {
    const count = summary.lowStock;
    if (count === 0)
      return {
        iconColor: 'text-gray-600 dark:text-gray-400',
        bgColor: 'bg-gray-50 dark:bg-gray-950',
      };
    if (count <= 10)
      return {
        iconColor: 'text-yellow-600 dark:text-yellow-400',
        bgColor: 'bg-yellow-50 dark:bg-yellow-950',
      };
    if (count <= 50)
      return {
        iconColor: 'text-orange-600 dark:text-orange-400',
        bgColor: 'bg-orange-50 dark:bg-orange-950',
      };
    return { iconColor: 'text-red-600 dark:text-red-400', bgColor: 'bg-red-50 dark:bg-red-950' };
  }, [summary.lowStock]);

  const cards: SummaryCard[] = [
    {
      label: 'Total Products',
      value: isLoading ? '—' : summary.totalProducts.toLocaleString(),
      icon: Package,
      iconColor: 'text-blue-600 dark:text-blue-400',
      bgColor: 'bg-blue-50 dark:bg-blue-950',
      description: 'Products tracked',
    },
    {
      label: 'Low Stock Alerts',
      value: isLoading ? '—' : summary.lowStock.toLocaleString(),
      icon: AlertTriangle,
      iconColor: lowStockSeverity.iconColor,
      bgColor: lowStockSeverity.bgColor,
      description: 'Needs attention',
    },
    {
      label: 'Out of Stock',
      value: isLoading ? '—' : summary.outOfStock.toLocaleString(),
      icon: XCircle,
      iconColor: 'text-red-600 dark:text-red-400',
      bgColor: 'bg-red-50 dark:bg-red-950',
      description: 'Immediate action',
    },
    {
      label: 'Total Valuation',
      value: isLoading
        ? '—'
        : `₨ ${summary.totalValue.toLocaleString(undefined, { minimumFractionDigits: 2 })}`,
      icon: DollarSign,
      iconColor: 'text-green-600 dark:text-green-400',
      bgColor: 'bg-green-50 dark:bg-green-950',
      description: 'Inventory value',
    },
  ];

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-28 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div
            key={card.label}
            className="rounded-lg border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-900"
          >
            <div className="flex items-center gap-3">
              <div className={cn('rounded-lg p-2', card.bgColor)}>
                <Icon className={cn('h-5 w-5', card.iconColor)} />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{card.label}</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{card.value}</p>
                <p className="text-xs text-gray-400 dark:text-gray-500">{card.description}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
