'use client';

import * as React from 'react';
import { Minus, Plus } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

export interface NumberInputProps {
  value?: number;
  onChange?: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

function clamp(val: number, min?: number, max?: number): number {
  if (min !== undefined && val < min) return min;
  if (max !== undefined && val > max) return max;
  return val;
}

function NumberInput({
  value,
  onChange,
  min,
  max,
  step = 1,
  disabled = false,
  placeholder = '0',
  className,
}: NumberInputProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value;
    if (raw === '' || raw === '-') {
      onChange?.(0);
      return;
    }
    const num = parseFloat(raw);
    if (!isNaN(num)) {
      onChange?.(clamp(num, min, max));
    }
  };

  const increment = () => {
    const next = (value ?? 0) + step;
    onChange?.(clamp(next, min, max));
  };

  const decrement = () => {
    const next = (value ?? 0) - step;
    onChange?.(clamp(next, min, max));
  };

  const atMin = min !== undefined && (value ?? 0) <= min;
  const atMax = max !== undefined && (value ?? 0) >= max;

  return (
    <div className={cn('flex items-center gap-0', className)}>
      <Button
        type="button"
        variant="outline"
        size="icon"
        className="h-10 w-10 shrink-0 rounded-r-none"
        onClick={decrement}
        disabled={disabled || atMin}
        aria-label="Decrease"
      >
        <Minus className="h-4 w-4" />
      </Button>
      <Input
        type="number"
        value={value ?? ''}
        onChange={handleChange}
        min={min}
        max={max}
        step={step}
        disabled={disabled}
        placeholder={placeholder}
        className="rounded-none border-x-0 text-center [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
        aria-label="Number input"
      />
      <Button
        type="button"
        variant="outline"
        size="icon"
        className="h-10 w-10 shrink-0 rounded-l-none"
        onClick={increment}
        disabled={disabled || atMax}
        aria-label="Increase"
      >
        <Plus className="h-4 w-4" />
      </Button>
    </div>
  );
}

export { NumberInput };
