'use client';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Banknote, Building2, CreditCard, FileText, Globe } from 'lucide-react';
import { paymentMethods, type PaymentMethodValue } from '@/lib/validations/payment';

const iconMap: Record<string, React.ElementType> = {
  Banknote,
  Building2,
  CreditCard,
  FileText,
  Globe,
};

interface PaymentMethodSelectProps {
  value?: string;
  onChange: (value: PaymentMethodValue) => void;
  error?: string;
}

export function PaymentMethodSelect({ value, onChange, error }: PaymentMethodSelectProps) {
  return (
    <div className="space-y-1.5">
      <Label>Payment Method *</Label>
      <Select value={value} onValueChange={(v) => onChange(v as PaymentMethodValue)}>
        <SelectTrigger className={error ? 'border-red-500' : ''}>
          <SelectValue placeholder="Select method" />
        </SelectTrigger>
        <SelectContent>
          {paymentMethods.map((method) => {
            const Icon = iconMap[method.icon];
            return (
              <SelectItem key={method.value} value={method.value}>
                <span className="flex items-center gap-2">
                  {Icon && <Icon className="h-4 w-4 text-gray-500" />}
                  {method.label}
                </span>
              </SelectItem>
            );
          })}
        </SelectContent>
      </Select>
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}
