'use client';

import { TotalCustomersCard } from './TotalCustomersCard';
import { ActiveCustomersCard } from './ActiveCustomersCard';
import { CreditOutstandingCard } from './CreditOutstandingCard';
import { useCustomers } from '@/hooks/crm/useCustomers';

export function CustomerSummaryCards() {
  const { data, isLoading } = useCustomers({ pageSize: 1 });

  const total = data?.pagination?.totalCount ?? 0;

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <TotalCustomersCard total={total} loading={isLoading} />
      <ActiveCustomersCard active={total} total={total} loading={isLoading} />
      <CreditOutstandingCard amount={0} loading={isLoading} />
    </div>
  );
}
