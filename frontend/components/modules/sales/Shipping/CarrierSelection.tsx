'use client';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { carriers, type CarrierValue } from '@/lib/validations/shipping';

interface CarrierSelectionProps {
  value?: string;
  onChange: (value: CarrierValue) => void;
  error?: string;
}

export function CarrierSelection({ value, onChange, error }: CarrierSelectionProps) {
  return (
    <div className="space-y-1.5">
      <Label>Carrier *</Label>
      <Select value={value} onValueChange={(v) => onChange(v as CarrierValue)}>
        <SelectTrigger className={error ? 'border-red-500' : ''}>
          <SelectValue placeholder="Select carrier" />
        </SelectTrigger>
        <SelectContent>
          {carriers.map((carrier) => (
            <SelectItem key={carrier.value} value={carrier.value}>
              {carrier.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}
