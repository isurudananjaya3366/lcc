'use client';

import { ClipboardList } from 'lucide-react';
import { KPICard } from './KPICard';

interface PendingTasksProps {
  pendingCount?: number;
  isLoading?: boolean;
}

export function PendingTasks({ pendingCount = 0, isLoading }: PendingTasksProps) {
  const variant = pendingCount > 5 ? 'warning' : 'default';

  return (
    <KPICard
      title="Pending Approvals"
      value={pendingCount.toLocaleString()}
      icon={ClipboardList}
      trend={
        pendingCount > 0
          ? { value: pendingCount, direction: 'neutral', label: 'awaiting action' }
          : undefined
      }
      href="/tasks"
      variant={variant}
      isLoading={isLoading}
    />
  );
}
