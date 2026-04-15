'use client';

import { Users } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface TotalCustomersCardProps {
  total: number;
  loading?: boolean;
}

export function TotalCustomersCard({ total, loading }: TotalCustomersCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Total Customers</CardTitle>
        <Users className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="h-8 w-20 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
        ) : (
          <div className="text-2xl font-bold">{total.toLocaleString()}</div>
        )}
      </CardContent>
    </Card>
  );
}
