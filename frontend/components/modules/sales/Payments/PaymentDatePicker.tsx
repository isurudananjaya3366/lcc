'use client';

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';

interface PaymentDatePickerProps {
  value: string;
  onChange: (value: string) => void;
  error?: string;
}

function toISODate(date: Date): string {
  return date.toISOString().split('T')[0] ?? '';
}

export function PaymentDatePicker({ value, onChange, error }: PaymentDatePickerProps) {
  const today = toISODate(new Date());
  const yesterday = toISODate(new Date(Date.now() - 86400000));

  return (
    <div className="space-y-1.5">
      <Label>Payment Date *</Label>
      <Input
        type="date"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        max={today}
        className={error ? 'border-red-500' : ''}
      />
      <div className="flex gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="text-xs"
          onClick={() => onChange(today)}
        >
          Today
        </Button>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="text-xs"
          onClick={() => onChange(yesterday)}
        >
          Yesterday
        </Button>
      </div>
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}
