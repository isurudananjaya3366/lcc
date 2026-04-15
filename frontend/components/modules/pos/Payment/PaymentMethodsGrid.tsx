'use client';

import { Banknote, CreditCard, Building2 } from 'lucide-react';
import type { PaymentMethod } from '../types';

const METHODS: Array<{
  id: PaymentMethod;
  label: string;
  icon: React.ReactNode;
}> = [
  { id: 'cash', label: 'Cash', icon: <Banknote className="h-5 w-5" /> },
  { id: 'card', label: 'Card', icon: <CreditCard className="h-5 w-5" /> },
  { id: 'bank_transfer', label: 'Bank Transfer', icon: <Building2 className="h-5 w-5" /> },
];

interface PaymentMethodsGridProps {
  selected: PaymentMethod;
  onSelect: (method: PaymentMethod) => void;
}

export function PaymentMethodsGrid({ selected, onSelect }: PaymentMethodsGridProps) {
  return (
    <div className="grid grid-cols-3 gap-2">
      {METHODS.map((method) => (
        <button
          key={method.id}
          onClick={() => onSelect(method.id)}
          className={`flex flex-col items-center gap-1 rounded-lg border px-3 py-3 text-sm font-medium transition-all ${
            selected === method.id
              ? 'border-primary bg-primary/5 text-primary'
              : 'border-gray-200 text-gray-600 hover:border-gray-300 dark:border-gray-700 dark:text-gray-400 dark:hover:border-gray-600'
          }`}
        >
          {method.icon}
          <span>{method.label}</span>
        </button>
      ))}
    </div>
  );
}
