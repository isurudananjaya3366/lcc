'use client';

import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

interface PaymentNotesFieldProps {
  value?: string;
  onChange: (value: string) => void;
  error?: string;
}

export function PaymentNotesField({ value, onChange, error }: PaymentNotesFieldProps) {
  const charCount = value?.length ?? 0;

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <Label>Notes</Label>
        <span className="text-xs text-gray-400">{charCount}/500</span>
      </div>
      <Textarea
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Add payment notes..."
        rows={3}
        maxLength={500}
        className={error ? 'border-red-500' : ''}
      />
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}
