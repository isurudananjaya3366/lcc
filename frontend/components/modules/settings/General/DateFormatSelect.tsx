'use client';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Label } from '@/components/ui/label';

const DATE_FORMATS = [
  { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY (25/01/2026)' },
  { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY (01/25/2026)' },
  { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD (2026-01-25)' },
  { value: 'DD-MM-YYYY', label: 'DD-MM-YYYY (25-01-2026)' },
  { value: 'DD.MM.YYYY', label: 'DD.MM.YYYY (25.01.2026)' },
];

interface DateFormatSelectProps {
  value: string;
  onChange: (value: string) => void;
}

export function DateFormatSelect({ value, onChange }: DateFormatSelectProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor="dateFormat">Date Format</Label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger id="dateFormat">
          <SelectValue placeholder="Select date format" />
        </SelectTrigger>
        <SelectContent>
          {DATE_FORMATS.map((f) => (
            <SelectItem key={f.value} value={f.value}>
              {f.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
