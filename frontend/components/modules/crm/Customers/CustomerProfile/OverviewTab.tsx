'use client';

import type { Customer } from '@/types/customer';
import { ContactInfoCard } from './ContactInfoCard';
import { CreditInfoCard } from './CreditInfoCard';

interface OverviewTabProps {
  customerId: string;
  customer?: Customer;
  onEdit?: () => void;
  onAdjustCredit?: () => void;
}

export function OverviewTab({ customer, onEdit, onAdjustCredit }: OverviewTabProps) {
  if (!customer) return null;

  const primaryAddress = customer.addresses?.find((a) => a.isDefault);
  const addressStr = primaryAddress
    ? [primaryAddress.street, primaryAddress.city, primaryAddress.state, primaryAddress.postalCode]
        .filter(Boolean)
        .join(', ')
    : undefined;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <ContactInfoCard
        customer={{
          phone: customer.phone || customer.mobile,
          email: customer.email,
          address: addressStr,
          type: customer.customerType,
        }}
        editable
        onEdit={onEdit}
      />
      <CreditInfoCard
        customer={{
          creditLimit: customer.creditLimit?.creditLimit ?? 0,
          creditUsed: customer.creditLimit?.currentBalance ?? 0,
          paymentTerms: customer.creditLimit?.paymentTerms,
        }}
        editable
        onAdjustCredit={onAdjustCredit}
      />
    </div>
  );
}
