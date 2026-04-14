'use client';

import { AlertTriangle } from 'lucide-react';
import { KPICard } from './KPICard';

interface LowStockAlertProps {
  lowStockCount?: number;
  criticalCount?: number;
  isLoading?: boolean;
}

export function LowStockAlert({
  lowStockCount = 0,
  criticalCount = 0,
  isLoading,
}: LowStockAlertProps) {
  const variant = criticalCount > 0 ? 'danger' : lowStockCount > 0 ? 'warning' : 'default';
  const label = criticalCount > 0 ? `${criticalCount} critical` : 'items low';

  return (
    <KPICard
      title="Low Stock Items"
      value={lowStockCount.toLocaleString()}
      icon={AlertTriangle}
      trend={{
        value: criticalCount,
        direction: criticalCount > 0 ? 'down' : 'neutral',
        label,
      }}
      href="/inventory/products?filter=low-stock"
      variant={variant}
      isLoading={isLoading}
    />
  );
}
