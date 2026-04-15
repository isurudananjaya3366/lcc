'use client';

import { UserCheck } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface ActiveCustomersCardProps {
  active: number;
  total: number;
  loading?: boolean;
}

export function ActiveCustomersCard({ active, total, loading }: ActiveCustomersCardProps) {
  const percentage = total > 0 ? ((active / total) * 100).toFixed(1) : '0';

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Active Customers</CardTitle>
        <UserCheck className="h-4 w-4 text-green-500" />
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="h-8 w-20 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
        ) : (
          <>
            <div className="text-2xl font-bold">{active.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">{percentage}% of total</p>
          </>
        )}
      </CardContent>
    </Card>
  );
}
