'use client';

import { forwardRef, useState, type InputHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

interface PriceInputProps extends Omit<
  InputHTMLAttributes<HTMLInputElement>,
  'value' | 'onChange'
> {
  value: number | string;
  onChange: (value: number) => void;
  onBlur?: () => void;
  prefix?: string;
  decimals?: number;
  error?: boolean;
}

function formatDisplay(value: number, decimals: number): string {
  if (isNaN(value)) return '';
  return new Intl.NumberFormat('en-LK', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

function parseNumeric(input: string): number {
  const cleaned = input.replace(/[^0-9.]/g, '');
  const parsed = parseFloat(cleaned);
  return isNaN(parsed) ? 0 : parsed;
}

export const PriceInput = forwardRef<HTMLInputElement, PriceInputProps>(
  (
    { value, onChange, onBlur, prefix = 'LKR', decimals = 2, error, className, disabled, ...props },
    ref
  ) => {
    const numericValue = typeof value === 'string' ? parseNumeric(value) : value;
    const [isFocused, setIsFocused] = useState(false);
    const [displayValue, setDisplayValue] = useState(formatDisplay(numericValue, decimals));

    const handleFocus = () => {
      setIsFocused(true);
      setDisplayValue(numericValue === 0 ? '' : String(numericValue));
    };

    const handleBlur = () => {
      setIsFocused(false);
      const parsed = parseNumeric(displayValue);
      const rounded = Math.round(parsed * Math.pow(10, decimals)) / Math.pow(10, decimals);
      onChange(rounded);
      setDisplayValue(formatDisplay(rounded, decimals));
      onBlur?.();
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const raw = e.target.value;
      // Allow only digits and a single decimal point
      if (/^[0-9]*\.?[0-9]*$/.test(raw) || raw === '') {
        setDisplayValue(raw);
        const parsed = parseNumeric(raw);
        onChange(parsed);
      }
    };

    return (
      <div className="relative">
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-sm font-medium text-gray-500 dark:text-gray-400">
          {prefix}
        </span>
        <input
          ref={ref}
          type="text"
          inputMode="decimal"
          value={isFocused ? displayValue : formatDisplay(numericValue, decimals)}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          disabled={disabled}
          className={cn(
            'flex h-10 w-full rounded-md border border-input bg-background pl-12 pr-3 py-2 text-right text-sm tabular-nums ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
            error && 'border-red-500 focus-visible:ring-red-500',
            className
          )}
          {...props}
        />
      </div>
    );
  }
);

PriceInput.displayName = 'PriceInput';
