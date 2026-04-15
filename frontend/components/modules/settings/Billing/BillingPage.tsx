'use client';

import { useState } from 'react';
import { CurrentPlanCard } from './CurrentPlanCard';
import { PlanSelectionModal } from './PlanSelectionModal';
import { BillingHistoryTable } from './BillingHistoryTable';
import { PaymentMethodSection } from './PaymentMethodSection';
import { AddPaymentMethodModal } from './AddPaymentMethodModal';
import type { SubscriptionPlan, BillingInvoice, PaymentMethod } from '@/types/settings';

// Mock data for UI development
const MOCK_PLAN: SubscriptionPlan = {
  id: 'business',
  name: 'Business',
  price: 4999,
  currency: 'LKR',
  interval: 'monthly',
  features: [
    'Up to 5 team members',
    'Up to 1,000 products',
    '5,000 transactions/month',
    '3 business locations',
    'Email + Chat support',
    'Standard integrations',
  ],
  maxUsers: 5,
  maxProducts: 1000,
  isCurrent: true,
};

const MOCK_INVOICES: BillingInvoice[] = [
  {
    id: '001',
    date: '2026-01-15',
    amount: 4999,
    currency: 'LKR',
    status: 'PAID',
  },
  {
    id: '002',
    date: '2025-12-15',
    amount: 4999,
    currency: 'LKR',
    status: 'PAID',
  },
  {
    id: '003',
    date: '2025-11-15',
    amount: 4999,
    currency: 'LKR',
    status: 'PAID',
  },
  {
    id: '004',
    date: '2025-10-15',
    amount: 4999,
    currency: 'LKR',
    status: 'PENDING',
  },
  {
    id: '005',
    date: '2025-09-15',
    amount: 4999,
    currency: 'LKR',
    status: 'FAILED',
  },
];

const MOCK_PAYMENT_METHODS: PaymentMethod[] = [
  {
    id: 'pm-1',
    type: 'card',
    last4: '1234',
    brand: 'visa',
    expiryMonth: 12,
    expiryYear: 2027,
    isDefault: true,
  },
  {
    id: 'pm-2',
    type: 'card',
    last4: '5678',
    brand: 'mastercard',
    expiryMonth: 6,
    expiryYear: 2026,
    isDefault: false,
  },
];

export function BillingPage() {
  const [showPlanModal, setShowPlanModal] = useState(false);
  const [showAddPaymentModal, setShowAddPaymentModal] = useState(false);
  const [paymentMethods, setPaymentMethods] = useState(MOCK_PAYMENT_METHODS);

  const handleSelectPlan = (planId: string) => {
    console.log('Selected plan:', planId);
    setShowPlanModal(false);
  };

  const handleSetDefault = (id: string) => {
    setPaymentMethods((prev) => prev.map((pm) => ({ ...pm, isDefault: pm.id === id })));
  };

  const handleRemovePaymentMethod = (id: string) => {
    setPaymentMethods((prev) => prev.filter((pm) => pm.id !== id));
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Billing & Plans</h1>
        <p className="text-muted-foreground">
          Manage your subscription plan, billing history, and payment methods.
        </p>
      </div>

      <CurrentPlanCard
        plan={MOCK_PLAN}
        nextBillingDate="February 15, 2026"
        onUpgrade={() => setShowPlanModal(true)}
        onCancel={() => console.log('Cancel subscription')}
      />

      <BillingHistoryTable invoices={MOCK_INVOICES} />

      <PaymentMethodSection
        paymentMethods={paymentMethods}
        onAddClick={() => setShowAddPaymentModal(true)}
        onSetDefault={handleSetDefault}
        onRemove={handleRemovePaymentMethod}
      />

      <PlanSelectionModal
        isOpen={showPlanModal}
        onClose={() => setShowPlanModal(false)}
        currentPlan={MOCK_PLAN.name}
        onSelectPlan={handleSelectPlan}
      />

      <AddPaymentMethodModal
        isOpen={showAddPaymentModal}
        onClose={() => setShowAddPaymentModal(false)}
        onSuccess={() => console.log('Payment method added')}
      />
    </div>
  );
}
