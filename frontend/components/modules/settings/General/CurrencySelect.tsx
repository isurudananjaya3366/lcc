'use client';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';

const CURRENCIES = [
  { value: 'LKR', label: 'LKR - Sri Lankan Rupees (₨)' },
  { value: 'USD', label: 'USD - US Dollar ($)' },
  { value: 'EUR', label: 'EUR - Euro (€)' },
  { value: 'GBP', label: 'GBP - British Pound (£)' },
  { value: 'INR', label: 'INR - Indian Rupee (₹)' },
  { value: 'AUD', label: 'AUD - Australian Dollar (A$)' },
  { value: 'SGD', label: 'SGD - Singapore Dollar (S$)' },
  { value: 'AED', label: 'AED - UAE Dirham (د.إ)' },
];

interface CurrencySelectProps {
  value: string;
  onChange: (value: string) => void;
}

export function CurrencySelect({ value, onChange }: CurrencySelectProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor="currency">Currency</Label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger id="currency">
          <SelectValue placeholder="Select currency" />
        </SelectTrigger>
        <SelectContent>
          {CURRENCIES.map((c) => (
            <SelectItem key={c.value} value={c.value}>
              {c.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
