'use client';

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';

interface AmountInputProps {
  value: number;
  onChange: (value: number) => void;
  amountDue: number;
  error?: string;
}

function formatCurrency(amount: number): string {
  return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

export function AmountInput({ value, onChange, amountDue, error }: AmountInputProps) {
  return (
    <div className="space-y-1.5">
      <Label>Amount (₨) *</Label>
      <Input
        type="number"
        min={0}
        step="0.01"
        value={value || ''}
        onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
        className={error ? 'border-red-500' : ''}
        placeholder="0.00"
      />
      <div className="flex items-center gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="text-xs"
          onClick={() => onChange(amountDue)}
        >
          Full ({formatCurrency(amountDue)})
        </Button>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="text-xs"
          onClick={() => onChange(Math.round((amountDue / 2) * 100) / 100)}
        >
          Half
        </Button>
      </div>
      {amountDue > 0 && (
        <p className="text-xs text-gray-500">Amount due: {formatCurrency(amountDue)}</p>
      )}
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}
