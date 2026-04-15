'use client';

import { Card, CardContent } from '@/components/ui/card';
import type { LeaveBalance } from '@/types/hr';

interface LeaveBalanceCardProps {
  balance: LeaveBalance;
}

const typeColors: Record<string, { bg: string; text: string }> = {
  ANNUAL: { bg: 'bg-blue-50 dark:bg-blue-950', text: 'text-blue-600' },
  SICK: { bg: 'bg-red-50 dark:bg-red-950', text: 'text-red-600' },
  UNPAID: { bg: 'bg-gray-50 dark:bg-gray-950', text: 'text-gray-600' },
  MATERNITY: { bg: 'bg-pink-50 dark:bg-pink-950', text: 'text-pink-600' },
  PATERNITY: { bg: 'bg-purple-50 dark:bg-purple-950', text: 'text-purple-600' },
  BEREAVEMENT: { bg: 'bg-stone-50 dark:bg-stone-950', text: 'text-stone-600' },
  STUDY: { bg: 'bg-indigo-50 dark:bg-indigo-950', text: 'text-indigo-600' },
};

export function LeaveBalanceCard({ balance }: LeaveBalanceCardProps) {
  const colors = typeColors[balance.leaveType] ?? typeColors.ANNUAL!;
  const usedPct =
    balance.totalEntitlement > 0 ? Math.round((balance.used / balance.totalEntitlement) * 100) : 0;

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">{balance.leaveType.replace('_', ' ')}</span>
          <span className={`text-xs ${colors.text}`}>{usedPct}% used</span>
        </div>
        <div className="mt-2">
          <span className="text-2xl font-bold">{balance.remaining}</span>
          <span className="text-sm text-muted-foreground"> / {balance.totalEntitlement} days</span>
        </div>
        <div className="mt-2 h-2 rounded-full bg-muted">
          <div
            className={`h-full rounded-full ${colors.bg} ${colors.text}`}
            style={{
              width: `${usedPct}%`,
              backgroundColor: 'currentColor',
              opacity: 0.6,
            }}
          />
        </div>
        <div className="mt-2 flex justify-between text-xs text-muted-foreground">
          <span>{balance.used} used</span>
          {balance.pending > 0 && <span>{balance.pending} pending</span>}
        </div>
      </CardContent>
    </Card>
  );
}
