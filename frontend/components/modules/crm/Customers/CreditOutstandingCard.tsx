'use client';

import { CreditCard } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface CreditOutstandingCardProps {
  amount: number;
  loading?: boolean;
}

export function CreditOutstandingCard({ amount, loading }: CreditOutstandingCardProps) {
  const formatted = amount.toLocaleString('en-LK', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Credit Outstanding</CardTitle>
        <CreditCard className="h-4 w-4 text-amber-500" />
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="h-8 w-24 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
        ) : (
          <div className="text-2xl font-bold">₨{formatted}</div>
        )}
      </CardContent>
    </Card>
  );
}
