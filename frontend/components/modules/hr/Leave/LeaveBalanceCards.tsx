'use client';

import { LeaveBalanceCard } from './LeaveBalanceCard';
import type { LeaveBalance } from '@/types/hr';

interface LeaveBalanceCardsProps {
  balances: LeaveBalance[];
}

export function LeaveBalanceCards({ balances }: LeaveBalanceCardsProps) {
  if (balances.length === 0) {
    return (
      <div className="text-center text-sm text-muted-foreground py-4">
        No leave balance data available.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
      {balances.map((balance) => (
        <LeaveBalanceCard key={balance.id} balance={balance} />
      ))}
    </div>
  );
}
