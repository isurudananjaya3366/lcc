'use client';

import * as React from 'react';

import { cn } from '@/lib/utils';
import { Input } from '@/components/ui/input';

export interface MoneyInputProps {
  value?: number;
  onChange?: (value: number | undefined) => void;
  currency?: string;
  currencySymbol?: string;
  decimals?: number;
  min?: number;
  max?: number;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

function formatMoney(value: number, decimals: number): string {
  const parts = value.toFixed(decimals).split('.');
  if (parts[0] !== undefined) {
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }
  return parts.join('.');
}

function parseMoney(text: string): number {
  const cleaned = text.replace(/[^0-9.-]/g, '');
  const parsed = parseFloat(cleaned);
  return isNaN(parsed) ? 0 : parsed;
}

function MoneyInput({
  value,
  onChange,
  currency = 'LKR',
  currencySymbol = 'Rs.',
  decimals = 2,
  min,
  max,
  disabled = false,
  placeholder = '0.00',
  className,
}: MoneyInputProps) {
  const [displayValue, setDisplayValue] = React.useState(
    value !== undefined ? formatMoney(value, decimals) : ''
  );

  React.useEffect(() => {
    if (value !== undefined) {
      setDisplayValue(formatMoney(value, decimals));
    }
  }, [value, decimals]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/[^0-9.]/g, '');
    setDisplayValue(raw);
  };

  const handleBlur = () => {
    let parsed = parseMoney(displayValue);
    if (min !== undefined && parsed < min) parsed = min;
    if (max !== undefined && parsed > max) parsed = max;
    setDisplayValue(formatMoney(parsed, decimals));
    onChange?.(parsed);
  };

  return (
    <Input
      type="text"
      inputMode="decimal"
      value={displayValue}
      onChange={handleChange}
      onBlur={handleBlur}
      disabled={disabled}
      placeholder={placeholder}
      addonBefore={currencySymbol}
      className={cn('text-right', className)}
      aria-label={`Amount in ${currency}`}
    />
  );
}

export { MoneyInput };
