'use client';

import type { DiscountType } from '../types';

interface DiscountValueInputProps {
  value: string;
  type: DiscountType;
  onChange: (value: string) => void;
}

export function DiscountValueInput({ value, type, onChange }: DiscountValueInputProps) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
        {type === 'percentage' ? 'Percentage (0-100)' : 'Amount (₨)'}
      </label>
      <input
        type="number"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={type === 'percentage' ? 'e.g. 10' : 'e.g. 100.00'}
        className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
        min={0}
        max={type === 'percentage' ? 100 : undefined}
        step={type === 'percentage' ? 1 : 0.01}
      />
    </div>
  );
}
