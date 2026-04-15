'use client';

import type { DiscountType } from '../types';

interface DiscountTypeToggleProps {
  value: DiscountType;
  onChange: (type: DiscountType) => void;
}

export function DiscountTypeToggle({ value, onChange }: DiscountTypeToggleProps) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
        Discount Type
      </label>
      <div className="flex rounded-md border border-gray-300 dark:border-gray-600">
        <button
          onClick={() => onChange('percentage')}
          className={`flex-1 rounded-l-md px-3 py-2 text-sm font-medium transition-colors ${
            value === 'percentage'
              ? 'bg-primary text-primary-foreground'
              : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700'
          }`}
        >
          Percentage (%)
        </button>
        <button
          onClick={() => onChange('fixed')}
          className={`flex-1 rounded-r-md px-3 py-2 text-sm font-medium transition-colors ${
            value === 'fixed'
              ? 'bg-primary text-primary-foreground'
              : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700'
          }`}
        >
          Fixed Amount (₨)
        </button>
      </div>
    </div>
  );
}
