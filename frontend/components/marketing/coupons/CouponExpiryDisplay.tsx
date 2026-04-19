'use client';

import { Clock, AlertTriangle } from 'lucide-react';
import { validateCouponExpiry } from '@/lib/marketing/couponValidation';
import { COUPON_TEST_IDS } from '@/lib/marketing/marketingTestIds';

interface CouponExpiryDisplayProps {
  startDate: string;
  endDate: string;
  className?: string;
}

export function CouponExpiryDisplay({ startDate, endDate, className = '' }: CouponExpiryDisplayProps) {
  const expiry = validateCouponExpiry(startDate, endDate);

  if (expiry.isExpired) {
    return (
      <span data-testid={COUPON_TEST_IDS.couponExpiryDisplay} className={`inline-flex items-center gap-1 text-xs text-red-500 ${className}`}>
        <Clock className="h-3 w-3" /> Expired
      </span>
    );
  }

  if (expiry.isNotStarted) {
    return (
      <span data-testid={COUPON_TEST_IDS.couponExpiryDisplay} className={`inline-flex items-center gap-1 text-xs text-gray-500 ${className}`}>
        <Clock className="h-3 w-3" /> {expiry.message}
      </span>
    );
  }

  const hours = Math.floor(expiry.timeRemaining / (1000 * 60 * 60));
  const days = Math.floor(hours / 24);
  const timeText = days > 0 ? `${days}d left` : `${hours}h left`;

  const urgencyColors = { high: 'text-red-500', medium: 'text-orange-500', low: 'text-gray-500', none: 'text-gray-500' };

  return (
    <span
      data-testid={COUPON_TEST_IDS.couponExpiryDisplay}
      className={`inline-flex items-center gap-1 text-xs ${urgencyColors[expiry.urgencyLevel]} ${className}`}
    >
      {expiry.urgencyLevel === 'high' ? <AlertTriangle className="h-3 w-3" /> : <Clock className="h-3 w-3" />}
      {timeText}
    </span>
  );
}
