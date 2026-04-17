'use client';

import { useState, useEffect } from 'react';
import { useDebounce } from '@/hooks/useDebounce';
import { cn } from '@/lib/utils';
import { DecreaseButton } from './DecreaseButton';
import { IncreaseButton } from './IncreaseButton';
import { QuantityInput } from './QuantityInput';

interface QuantitySelectorProps {
  value: number;
  onChange: (qty: number) => void;
  min?: number;
  max?: number;
  disabled?: boolean;
}

export function QuantitySelector({
  value,
  onChange,
  min = 1,
  max = 99,
  disabled = false,
}: QuantitySelectorProps) {
  const [quantity, setQuantity] = useState(value);
  const debouncedQuantity = useDebounce(quantity, 500);

  // Sync external value
  useEffect(() => {
    setQuantity(value);
  }, [value]);

  // Fire onChange when debounced value changes
  useEffect(() => {
    if (debouncedQuantity !== value) {
      onChange(debouncedQuantity);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedQuantity]);

  const handleDecrease = () => {
    if (quantity > min) setQuantity((q) => q - 1);
  };

  const handleIncrease = () => {
    if (quantity < max) setQuantity((q) => q + 1);
  };

  const handleInputChange = (qty: number) => {
    setQuantity(qty);
  };

  return (
    <div className={cn('inline-flex items-center', disabled && 'opacity-50')} role="group" aria-label="Quantity selector">
      <DecreaseButton onClick={handleDecrease} disabled={disabled || quantity <= min} />
      <QuantityInput
        value={quantity}
        onChange={handleInputChange}
        min={min}
        max={max}
        disabled={disabled}
      />
      <IncreaseButton onClick={handleIncrease} disabled={disabled || quantity >= max} />
    </div>
  );
}
