'use client';

import { useState } from 'react';
import { Tag, Copy, Check, Clock } from 'lucide-react';
import type { CouponListItem } from '@/types/marketing/coupon.types';

interface CouponCardProps {
  coupon: CouponListItem;
  onApply?: (code: string) => void;
  className?: string;
}

export function CouponCard({ coupon, onApply, className = '' }: CouponCardProps) {
  const [copied, setCopied] = useState(false);

  const discountLabel =
    coupon.discountType === 'percentage'
      ? `${coupon.discountValue}% OFF`
      : coupon.discountType === 'free_shipping'
        ? 'Free Shipping'
        : `₨${coupon.discountValue.toLocaleString()} OFF`;

  const daysLeft = coupon.endDate
    ? Math.ceil((new Date(coupon.endDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
    : null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(coupon.code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for browsers that block clipboard
      const el = document.createElement('textarea');
      el.value = coupon.code;
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div
      className={`relative overflow-hidden rounded-xl border-2 border-dashed border-red-200 bg-red-50 p-4 ${className}`}
    >
      {/* Discount badge */}
      <div className="mb-3 flex items-center gap-2">
        <span className="rounded-full bg-red-600 px-3 py-1 text-sm font-bold text-white">{discountLabel}</span>
      </div>

      {/* Description */}
      <p className="mb-3 text-sm text-gray-600">{coupon.description}</p>

      {/* Code row */}
      <div className="flex items-center gap-2">
        <div className="flex flex-1 items-center gap-2 rounded-lg border border-red-200 bg-white px-3 py-2">
          <Tag className="h-4 w-4 flex-shrink-0 text-red-500" />
          <span className="flex-1 font-mono text-sm font-bold tracking-widest text-gray-800">{coupon.code}</span>
        </div>
        <button
          onClick={handleCopy}
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-600 transition-colors hover:bg-gray-50"
          aria-label="Copy coupon code"
        >
          {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
        </button>
        {onApply && (
          <button
            onClick={() => onApply(coupon.code)}
            type="button"
            className="rounded-lg bg-red-600 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-red-700"
          >
            Apply
          </button>
        )}
      </div>

      {/* Expiry */}
      {daysLeft !== null && daysLeft > 0 && daysLeft <= 7 && (
        <div className="mt-3 flex items-center gap-1 text-xs text-amber-600">
          <Clock className="h-3 w-3" />
          <span>Expires in {daysLeft} day{daysLeft !== 1 ? 's' : ''}</span>
        </div>
      )}
    </div>
  );
}
