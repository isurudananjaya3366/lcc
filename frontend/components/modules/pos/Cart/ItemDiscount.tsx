'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import type { POSDiscount, DiscountType } from '../types';

const DISCOUNT_REASONS = [
  'Loyalty Discount',
  'Damaged Item',
  'Manager Approval',
  'Promotion',
  'Bulk Purchase',
  'Other',
];

interface ItemDiscountProps {
  currentDiscount?: POSDiscount;
  unitPrice: number;
  quantity: number;
  onApply: (discount: POSDiscount) => void;
  onCancel: () => void;
}

export function ItemDiscount({
  currentDiscount,
  unitPrice,
  quantity,
  onApply,
  onCancel,
}: ItemDiscountProps) {
  const [type, setType] = useState<DiscountType>(currentDiscount?.type ?? 'percentage');
  const [value, setValue] = useState(String(currentDiscount?.value ?? ''));
  const [reason, setReason] = useState(currentDiscount?.reason ?? '');

  const numValue = parseFloat(value);
  const isValid = !isNaN(numValue) && numValue > 0 && (type !== 'percentage' || numValue <= 100);

  // Live preview
  const subtotal = unitPrice * quantity;
  const discountAmt = isValid
    ? type === 'percentage'
      ? subtotal * (numValue / 100)
      : Math.min(numValue, subtotal)
    : 0;
  const finalPrice = subtotal - discountAmt;

  const handleApply = () => {
    if (!isValid) return;
    onApply({
      type,
      value: numValue,
      reason: reason || undefined,
      appliedAt: new Date().toISOString(),
    });
  };

  return (
    <div className="mt-2 space-y-2 rounded border border-gray-200 bg-gray-50 p-2 dark:border-gray-700 dark:bg-gray-800">
      <div className="flex items-center gap-2">
        {/* Type Toggle */}
        <div className="flex rounded border border-gray-300 dark:border-gray-600">
          <button
            onClick={() => setType('percentage')}
            className={`px-2 py-1 text-xs font-medium ${type === 'percentage' ? 'bg-primary text-primary-foreground' : 'text-gray-600 dark:text-gray-400'}`}
          >
            %
          </button>
          <button
            onClick={() => setType('fixed')}
            className={`px-2 py-1 text-xs font-medium ${type === 'fixed' ? 'bg-primary text-primary-foreground' : 'text-gray-600 dark:text-gray-400'}`}
          >
            ₨
          </button>
        </div>

        {/* Value Input */}
        <input
          type="number"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={type === 'percentage' ? '0-100' : 'Amount'}
          className="w-20 rounded border border-gray-300 px-2 py-1 text-xs dark:border-gray-600 dark:bg-gray-700"
          min={0}
          max={type === 'percentage' ? 100 : undefined}
          step={type === 'percentage' ? 1 : 0.01}
          // eslint-disable-next-line jsx-a11y/no-autofocus
          autoFocus
        />

        {/* Reason Dropdown */}
        <select
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          className="min-w-0 flex-1 rounded border border-gray-300 px-2 py-1 text-xs dark:border-gray-600 dark:bg-gray-700"
        >
          <option value="">Select reason</option>
          {DISCOUNT_REASONS.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>

        {/* Actions */}
        <Button size="sm" className="h-7 text-xs" onClick={handleApply} disabled={!isValid}>
          Apply
        </Button>
        <Button size="sm" variant="ghost" className="h-7 text-xs" onClick={onCancel}>
          Cancel
        </Button>
      </div>

      {/* Live Preview */}
      {isValid && (
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <span>
            ₨ {subtotal.toLocaleString('en-LK', { minimumFractionDigits: 2 })} − ₨{' '}
            {discountAmt.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
          </span>
          <span className="font-medium text-gray-700 dark:text-gray-300">
            = ₨ {finalPrice.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
          </span>
        </div>
      )}
    </div>
  );
}
