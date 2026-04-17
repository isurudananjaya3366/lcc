'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { cn } from '@/lib/utils';

interface PriceRangeFilterProps {
  min?: number;
  max?: number;
  value: { min: number; max: number } | null;
  onChange: (range: { min: number; max: number } | null) => void;
  currency?: string;
}

export function PriceRangeFilter({
  min = 0,
  max = 50000,
  value,
  onChange,
  currency = '₨',
}: PriceRangeFilterProps) {
  const [localMin, setLocalMin] = useState<string>(value?.min?.toString() ?? '');
  const [localMax, setLocalMax] = useState<string>(value?.max?.toString() ?? '');
  const [error, setError] = useState<string | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Sync from parent
  useEffect(() => {
    setLocalMin(value?.min?.toString() ?? '');
    setLocalMax(value?.max?.toString() ?? '');
    setError(null);
  }, [value]);

  const emitChange = useCallback(
    (minStr: string, maxStr: string) => {
      if (debounceRef.current) clearTimeout(debounceRef.current);

      debounceRef.current = setTimeout(() => {
        const minVal = minStr === '' ? undefined : Number(minStr);
        const maxVal = maxStr === '' ? undefined : Number(maxStr);

        if (minVal == null && maxVal == null) {
          setError(null);
          onChange(null);
          return;
        }

        const effectiveMin = minVal ?? min;
        const effectiveMax = maxVal ?? max;

        if (effectiveMin > effectiveMax) {
          setError('Min must be less than max');
          return;
        }

        setError(null);
        onChange({ min: effectiveMin, max: effectiveMax });
      }, 500);
    },
    [onChange, min, max]
  );

  // Cleanup debounce
  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  const handleMinChange = (val: string) => {
    // Allow only numeric values
    const sanitized = val.replace(/[^0-9]/g, '');
    setLocalMin(sanitized);
    emitChange(sanitized, localMax);
  };

  const handleMaxChange = (val: string) => {
    const sanitized = val.replace(/[^0-9]/g, '');
    setLocalMax(sanitized);
    emitChange(localMin, sanitized);
  };

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Min Price</label>
          <div className="relative">
            <span className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-sm text-gray-400">
              {currency}
            </span>
            <input
              type="text"
              inputMode="numeric"
              value={localMin}
              onChange={(e) => handleMinChange(e.target.value)}
              placeholder={min.toString()}
              className={cn(
                'w-full rounded-md border py-2 pl-8 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                error ? 'border-red-300' : 'border-gray-300'
              )}
            />
          </div>
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Max Price</label>
          <div className="relative">
            <span className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-sm text-gray-400">
              {currency}
            </span>
            <input
              type="text"
              inputMode="numeric"
              value={localMax}
              onChange={(e) => handleMaxChange(e.target.value)}
              placeholder={max.toString()}
              className={cn(
                'w-full rounded-md border py-2 pl-8 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                error ? 'border-red-300' : 'border-gray-300'
              )}
            />
          </div>
        </div>
      </div>
      {error && <p className="text-xs text-red-500">{error}</p>}
      <p className="text-xs text-gray-400">
        Range: {currency}
        {min.toLocaleString()} — {currency}
        {max.toLocaleString()}
      </p>
    </div>
  );
}
