'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Skeleton } from '@/components/ui/skeleton';
import { useCustomer, useDeleteCustomer } from '@/hooks/crm/useCustomers';
import { CustomerHeader } from './CustomerProfile/CustomerHeader';
import { CustomerQuickStats } from './CustomerProfile/CustomerQuickStats';
import { CustomerTabs } from './CustomerProfile/CustomerTabs';
import { EditCustomerModal } from './CustomerProfile/EditCustomerModal';
import { AdjustCreditModal } from './CustomerProfile/AdjustCreditModal';

interface CustomerDetailsProps {
  customerId: string;
}

export function CustomerDetails({ customerId }: CustomerDetailsProps) {
  const router = useRouter();
  const { data, isLoading, isError } = useCustomer(customerId);
  const deleteCustomer = useDeleteCustomer();
  const [editOpen, setEditOpen] = useState(false);
  const [creditOpen, setCreditOpen] = useState(false);

  const customer = data?.data;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Skeleton className="h-24 w-24 rounded-full" />
          <div className="space-y-2">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-32" />
          </div>
        </div>
        <div className="grid grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-20" />
          ))}
        </div>
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (isError || !customer) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <h2 className="text-lg font-medium">Customer not found</h2>
        <p className="text-sm text-muted-foreground">
          The customer you&apos;re looking for doesn&apos;t exist or has been removed.
        </p>
      </div>
    );
  }

  function handleDelete() {
    if (!customer) return;
    deleteCustomer.mutate(customer.id, {
      onSuccess: () => router.push('/customers'),
    });
  }

  return (
    <div className="space-y-6">
      <CustomerHeader
        customer={customer}
        onEdit={() => setEditOpen(true)}
        onDelete={handleDelete}
      />

      <CustomerQuickStats
        customer={{
          totalSpent: customer.totalSpent,
          orderCount: customer.totalOrders,
          lastOrderDate: customer.lastOrderDate,
          memberSince: customer.createdAt,
        }}
      />

      <CustomerTabs
        customerId={customerId}
        customer={customer}
        onEdit={() => setEditOpen(true)}
        onAdjustCredit={() => setCreditOpen(true)}
      />

      <EditCustomerModal customer={customer} isOpen={editOpen} onClose={() => setEditOpen(false)} />

      <AdjustCreditModal
        customer={customer}
        isOpen={creditOpen}
        onClose={() => setCreditOpen(false)}
      />
    </div>
  );
}
