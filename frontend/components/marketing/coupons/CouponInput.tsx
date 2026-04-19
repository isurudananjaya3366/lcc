'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { Tag, Loader2, X, CheckCircle, XCircle } from 'lucide-react';
import { useCouponStore } from '@/stores/store/coupon';
import { useApplyCoupon } from '@/hooks/marketing/useCoupon';
import { COUPON_TEST_IDS } from '@/lib/marketing/marketingTestIds';

type ValidationState = 'idle' | 'validating' | 'valid' | 'invalid';

const COUPON_CODE_REGEX = /^[A-Z0-9_-]{3,30}$/;

interface CouponInputProps {
  cartTotal?: number;
  onApplied?: (code: string) => void;
  onError?: (message: string) => void;
  className?: string;
}

export function CouponInput({ cartTotal, onApplied, onError, className = '' }: CouponInputProps) {
  const [code, setCode] = useState('');
  const [validationState, setValidationState] = useState<ValidationState>('idle');
  const [validationMessage, setValidationMessage] = useState('');
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const { appliedCoupon } = useCouponStore();
  const { mutate: apply, isPending } = useApplyCoupon();

  // 500ms debounced format validation
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);

    if (!code.trim()) {
      setValidationState('idle');
      setValidationMessage('');
      return;
    }

    setValidationState('validating');
    debounceRef.current = setTimeout(() => {
      if (COUPON_CODE_REGEX.test(code.trim())) {
        setValidationState('valid');
        setValidationMessage('');
      } else {
        setValidationState('invalid');
        setValidationMessage('Invalid format — use letters, numbers, _ or -');
      }
    }, 500);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [code]);

  const handleApply = useCallback(() => {
    const trimmed = code.trim().toUpperCase();
    if (!trimmed || validationState === 'invalid') return;

    apply(
      { code: trimmed },
      {
        onSuccess: (res) => {
          if (res.success) {
            setCode('');
            setValidationState('idle');
            onApplied?.(trimmed);
          }
        },
        onError: (err) => {
          setValidationState('invalid');
          setValidationMessage(err.message);
          onError?.(err.message);
        },
      }
    );
  }, [code, validationState, apply, onApplied, onError]);

  if (appliedCoupon) return null;

  const borderClass =
    validationState === 'valid'
      ? 'border-green-500 focus:border-green-500 focus:ring-green-500'
      : validationState === 'invalid'
        ? 'border-red-400 focus:border-red-500 focus:ring-red-500'
        : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500';

  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Tag className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            data-testid={COUPON_TEST_IDS.couponInput}
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
            onKeyDown={(e) => e.key === 'Enter' && handleApply()}
            placeholder="Enter coupon code"
            className={`w-full rounded-lg border py-2 pl-10 pr-8 text-sm outline-none focus:ring-1 disabled:opacity-50 ${borderClass}`}
            disabled={isPending}
            maxLength={30}
            aria-describedby={validationMessage ? 'coupon-validation-msg' : undefined}
          />
          {/* Inline validation icon */}
          {code && !isPending && validationState === 'valid' && (
            <CheckCircle className="absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-green-500" />
          )}
          {code && !isPending && validationState === 'invalid' && (
            <XCircle className="absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-red-400" />
          )}
          {code && !isPending && validationState === 'idle' && (
            <button
              onClick={() => setCode('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              type="button"
            >
              <X className="h-4 w-4" />
            </button>
          )}
          {isPending && (
            <Loader2 className="absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-blue-500" />
          )}
        </div>
        <button
          data-testid={COUPON_TEST_IDS.couponApplyButton}
          onClick={handleApply}
          disabled={!code.trim() || isPending || validationState === 'invalid' || validationState === 'validating'}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          type="button"
        >
          Apply
        </button>
      </div>
      {validationMessage && (
        <p id="coupon-validation-msg" className="ml-1 text-xs text-red-500" role="alert">
          {validationMessage}
        </p>
      )}
    </div>
  );
}
