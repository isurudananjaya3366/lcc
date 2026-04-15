'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import type { POSDiscount, DiscountType } from '../types';

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

interface DiscountModalProps {
  open: boolean;
  onClose: () => void;
  onApply: (discount: POSDiscount) => void;
  onClear?: () => void;
  currentDiscount: POSDiscount | null;
  subtotal: number;
}

export function DiscountModal({
  open,
  onClose,
  onApply,
  onClear,
  currentDiscount,
  subtotal,
}: DiscountModalProps) {
  const [type, setType] = useState<DiscountType>('percentage');
  const [value, setValue] = useState('');
  const [reason, setReason] = useState('');
  const [customReason, setCustomReason] = useState('');

  // Reset state when modal opens
  useEffect(() => {
    if (open) {
      setType(currentDiscount?.type ?? 'percentage');
      setValue(currentDiscount?.value != null ? String(currentDiscount.value) : '');
      setReason(currentDiscount?.reason ?? '');
      setCustomReason('');
    }
  }, [open, currentDiscount]);

  const numValue = parseFloat(value);
  const isValid = !isNaN(numValue) && numValue > 0 && (type !== 'percentage' || numValue <= 100);

  // Live preview
  const discountAmt = isValid
    ? type === 'percentage'
      ? subtotal * (numValue / 100)
      : Math.min(numValue, subtotal)
    : 0;
  const finalTotal = subtotal - discountAmt;

  const handleApply = () => {
    if (!isValid) return;
    const finalReason = reason === 'Other' ? customReason || 'Other' : reason;
    onApply({
      type,
      value: numValue,
      reason: finalReason || undefined,
      appliedAt: new Date().toISOString(),
    });
  };

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle>Apply Cart Discount</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Type Toggle */}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
              Discount Type
            </label>
            <div className="flex rounded-md border border-gray-300 dark:border-gray-600">
              <button
                onClick={() => setType('percentage')}
                className={`flex-1 rounded-l-md px-3 py-2 text-sm font-medium transition-colors ${
                  type === 'percentage'
                    ? 'bg-primary text-primary-foreground'
                    : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700'
                }`}
              >
                Percentage (%)
              </button>
              <button
                onClick={() => setType('fixed')}
                className={`flex-1 rounded-r-md px-3 py-2 text-sm font-medium transition-colors ${
                  type === 'fixed'
                    ? 'bg-primary text-primary-foreground'
                    : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700'
                }`}
              >
                Fixed Amount (₨)
              </button>
            </div>
          </div>

          {/* Value Input */}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
              {type === 'percentage' ? 'Percentage (0-100)' : 'Amount (₨)'}
            </label>
            <input
              type="number"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder={type === 'percentage' ? 'e.g. 10' : 'e.g. 100.00'}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
              min={0}
              max={type === 'percentage' ? 100 : undefined}
              step={type === 'percentage' ? 1 : 0.01}
              // eslint-disable-next-line jsx-a11y/no-autofocus
              autoFocus
            />
          </div>

          {/* Reason Select */}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
              Reason
            </label>
            <select
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
            >
              <option value="">Select a reason...</option>
              {DISCOUNT_REASONS.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
            {reason === 'Other' && (
              <input
                type="text"
                value={customReason}
                onChange={(e) => setCustomReason(e.target.value)}
                placeholder="Enter custom reason..."
                className="mt-2 w-full rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
              />
            )}
          </div>

          {/* Live Preview */}
          {isValid && (
            <div className="rounded-md bg-gray-50 p-3 text-sm dark:bg-gray-800">
              <div className="flex justify-between text-gray-500 dark:text-gray-400">
                <span>Subtotal</span>
                <span>₨ {subtotal.toLocaleString('en-LK', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between text-green-600">
                <span>Discount</span>
                <span>− ₨ {discountAmt.toLocaleString('en-LK', { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="mt-1 flex justify-between border-t border-gray-200 pt-1 font-bold dark:border-gray-700">
                <span>Total</span>
                <span>₨ {finalTotal.toLocaleString('en-LK', { minimumFractionDigits: 2 })}</span>
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="gap-2">
          {currentDiscount && onClear && (
            <Button
              variant="ghost"
              className="mr-auto text-red-500 hover:text-red-600"
              onClick={onClear}
            >
              Clear
            </Button>
          )}
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleApply} disabled={!isValid}>
            Apply Discount
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
