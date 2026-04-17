'use client';

import { useState } from 'react';

interface QuantitySelectorProps {
  min?: number;
  max: number;
  value: number;
  onChange: (quantity: number) => void;
}

export function QuantitySelector({
  min = 1,
  max,
  value,
  onChange,
}: QuantitySelectorProps) {
  const [inputValue, setInputValue] = useState(String(value));

  const decrement = () => {
    if (value > min) {
      const next = value - 1;
      onChange(next);
      setInputValue(String(next));
    }
  };

  const increment = () => {
    if (value < max) {
      const next = value + 1;
      onChange(next);
      setInputValue(String(next));
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/\D/g, '');
    setInputValue(raw);
  };

  const handleBlur = () => {
    let num = parseInt(inputValue, 10);
    if (isNaN(num) || num < min) num = min;
    if (num > max) num = max;
    onChange(num);
    setInputValue(String(num));
  };

  return (
    <div>
      <label className="mb-2 block text-sm font-medium text-gray-900">Quantity</label>
      <div className="inline-flex items-center rounded-md border border-gray-300">
        <button
          onClick={decrement}
          disabled={value <= min}
          className="flex h-10 w-10 items-center justify-center text-gray-600 hover:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-300 rounded-l-md"
          aria-label="Decrease quantity"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14" />
          </svg>
        </button>

        <input
          type="text"
          inputMode="numeric"
          value={inputValue}
          onChange={handleInputChange}
          onBlur={handleBlur}
          className="h-10 w-14 border-x border-gray-300 text-center text-sm font-medium text-gray-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
          aria-label="Quantity"
        />

        <button
          onClick={increment}
          disabled={value >= max}
          className="flex h-10 w-10 items-center justify-center text-gray-600 hover:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-300 rounded-r-md"
          aria-label="Increase quantity"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
        </button>
      </div>
      {max <= 10 && (
        <p className="mt-1 text-xs text-gray-500">{max} available</p>
      )}
    </div>
  );
}
