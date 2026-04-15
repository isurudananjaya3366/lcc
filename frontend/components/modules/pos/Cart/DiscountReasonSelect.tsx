'use client';

import { useState } from 'react';

const DISCOUNT_REASONS = [
  'Customer request',
  'Price match',
  'Loyalty discount',
  'Staff discount',
  'Promotional offer',
  'Manager override',
  'Damaged item',
  'Other',
];

interface DiscountReasonSelectProps {
  value: string;
  onChange: (reason: string) => void;
}

export function DiscountReasonSelect({ value, onChange }: DiscountReasonSelectProps) {
  const [customReason, setCustomReason] = useState('');

  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
        Reason
      </label>
      <select
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
          if (e.target.value !== 'Other') setCustomReason('');
        }}
        className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
      >
        <option value="">Select a reason...</option>
        {DISCOUNT_REASONS.map((r) => (
          <option key={r} value={r}>
            {r}
          </option>
        ))}
      </select>
      {value === 'Other' && (
        <input
          type="text"
          value={customReason}
          onChange={(e) => {
            setCustomReason(e.target.value);
            onChange(`Other: ${e.target.value}`);
          }}
          placeholder="Enter custom reason..."
          className="mt-2 w-full rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
        />
      )}
    </div>
  );
}
