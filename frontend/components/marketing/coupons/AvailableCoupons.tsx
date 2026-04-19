'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp, Copy, Check, Tag } from 'lucide-react';
import { useAvailableCoupons } from '@/hooks/marketing/useCoupon';
import type { CouponListItem } from '@/types/marketing/coupon.types';
import { COUPON_TEST_IDS } from '@/lib/marketing/marketingTestIds';

interface AvailableCouponsProps {
  onSelectCoupon?: (code: string) => void;
  className?: string;
}

export function AvailableCoupons({ onSelectCoupon, className = '' }: AvailableCouponsProps) {
  const [expanded, setExpanded] = useState(false);
  const { data: coupons, isLoading } = useAvailableCoupons();

  if (isLoading || !coupons?.length) return null;

  return (
    <div className={className}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center justify-between text-sm text-blue-600 hover:text-blue-700"
        type="button"
      >
        <span>View available coupons ({coupons.length})</span>
        {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
      </button>

      {expanded && (
        <div data-testid={COUPON_TEST_IDS.availableCouponsList} className="mt-2 space-y-2">
          {coupons.map((coupon) => (
            <CouponCard key={coupon.id} coupon={coupon} onSelect={onSelectCoupon} />
          ))}
        </div>
      )}
    </div>
  );
}

function CouponCard({ coupon, onSelect }: { coupon: CouponListItem; onSelect?: (code: string) => void }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(coupon.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const discountLabel =
    coupon.discountType === 'percentage'
      ? `${coupon.discountValue}% off`
      : coupon.discountType === 'free_shipping'
        ? 'Free Shipping'
        : `₨${coupon.discountValue.toLocaleString()} off`;

  return (
    <div
      data-testid={COUPON_TEST_IDS.couponCard}
      className={`flex items-center justify-between rounded-lg border p-3 ${
        coupon.isApplicable ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-gray-50 opacity-60'
      }`}
    >
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <Tag className="h-3.5 w-3.5 text-green-600" />
          <span className="font-mono text-sm font-semibold">{coupon.code}</span>
          <button
            data-testid={COUPON_TEST_IDS.copyCouponButton}
            onClick={handleCopy}
            className="rounded p-0.5 text-gray-400 hover:text-gray-600"
            type="button"
            aria-label="Copy coupon code"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-green-500" /> : <Copy className="h-3.5 w-3.5" />}
          </button>
        </div>
        <p className="mt-0.5 text-xs text-gray-600">{coupon.description}</p>
        <div className="mt-1 flex items-center gap-2 text-xs text-gray-500">
          <span className="font-medium text-green-600">{discountLabel}</span>
          {coupon.minimumOrder && <span>• Min: ₨{coupon.minimumOrder.toLocaleString()}</span>}
        </div>
      </div>
      {coupon.isApplicable && onSelect && (
        <button
          onClick={() => onSelect(coupon.code)}
          className="ml-3 rounded-lg bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-700"
          type="button"
        >
          Apply
        </button>
      )}
    </div>
  );
}
