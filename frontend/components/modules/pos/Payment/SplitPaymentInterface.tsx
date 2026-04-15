'use client';

import { X, Banknote, CreditCard, Building2 } from 'lucide-react';
import type { POSPayment, PaymentMethod } from '../types';

const METHOD_ICONS: Record<PaymentMethod, React.ReactNode> = {
  cash: <Banknote className="h-4 w-4" />,
  card: <CreditCard className="h-4 w-4" />,
  bank_transfer: <Building2 className="h-4 w-4" />,
  mobile: <CreditCard className="h-4 w-4" />,
  store_credit: <CreditCard className="h-4 w-4" />,
};

const METHOD_LABELS: Record<PaymentMethod, string> = {
  cash: 'Cash',
  card: 'Card',
  bank_transfer: 'Bank Transfer',
  mobile: 'Mobile',
  store_credit: 'Store Credit',
};

interface SplitPaymentInterfaceProps {
  payments: POSPayment[];
  onRemove: (paymentId: string) => void;
  remaining: number;
}

export function SplitPaymentInterface({
  payments,
  onRemove,
  remaining,
}: SplitPaymentInterfaceProps) {
  return (
    <div className="space-y-2">
      <p className="text-xs font-medium text-gray-500 dark:text-gray-400">Payments Applied</p>
      {payments.map((p) => (
        <div
          key={p.id}
          className="flex items-center justify-between rounded-md border border-gray-200 px-3 py-2 text-sm dark:border-gray-700"
        >
          <div className="flex items-center gap-2">
            {METHOD_ICONS[p.method]}
            <span className="font-medium">{METHOD_LABELS[p.method]}</span>
            {p.reference && <span className="text-xs text-gray-400">({p.reference})</span>}
          </div>
          <div className="flex items-center gap-2">
            <span className="font-medium">
              ₨ {p.amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
            </span>
            <button
              onClick={() => onRemove(p.id)}
              className="rounded p-0.5 text-gray-400 hover:text-red-500"
              aria-label={`Remove ${METHOD_LABELS[p.method]} payment`}
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      ))}
      {remaining > 0 && (
        <p className="text-center text-xs text-amber-600 dark:text-amber-400">
          ₨ {remaining.toLocaleString('en-LK', { minimumFractionDigits: 2 })} remaining
        </p>
      )}
    </div>
  );
}
