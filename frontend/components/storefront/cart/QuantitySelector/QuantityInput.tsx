'use client';

import { useState, useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';

interface QuantityInputProps {
  value: number;
  onChange: (qty: number) => void;
  min?: number;
  max?: number;
  disabled?: boolean;
}

export function QuantityInput({
  value,
  onChange,
  min = 1,
  max = 99,
  disabled = false,
}: QuantityInputProps) {
  const [localValue, setLocalValue] = useState(String(value));
  const inputRef = useRef<HTMLInputElement>(null);

  // Sync external value when input is not focused
  useEffect(() => {
    if (document.activeElement !== inputRef.current) {
      setLocalValue(String(value));
    }
  }, [value]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalValue(e.target.value);
  };

  const handleBlur = () => {
    const parsed = parseInt(localValue, 10);
    if (isNaN(parsed) || parsed < min) {
      setLocalValue(String(min));
      onChange(min);
    } else if (parsed > max) {
      setLocalValue(String(max));
      onChange(max);
    } else {
      setLocalValue(String(parsed));
      onChange(parsed);
    }
  };

  return (
    <input
      ref={inputRef}
      type="number"
      value={localValue}
      onChange={handleChange}
      onBlur={handleBlur}
      onFocus={(e) => e.target.select()}
      min={min}
      max={max}
      disabled={disabled}
      aria-label="Item quantity"
      className={cn(
        'h-8 w-12 border-y border-gray-300 bg-white text-center text-sm',
        'focus:outline-none focus:ring-1 focus:ring-green-500',
        '[appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none',
        'dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200',
        disabled && 'cursor-not-allowed opacity-50'
      )}
    />
  );
}
