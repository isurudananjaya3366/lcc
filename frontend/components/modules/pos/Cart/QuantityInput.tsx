'use client';

import { useState, useRef, useEffect } from 'react';

interface QuantityInputProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
}

export function QuantityInput({ value, onChange, min = 1, max = 9999 }: QuantityInputProps) {
  const [editing, setEditing] = useState(false);
  const [inputValue, setInputValue] = useState(String(value));
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!editing) setInputValue(String(value));
  }, [value, editing]);

  useEffect(() => {
    if (editing) inputRef.current?.select();
  }, [editing]);

  const commit = () => {
    const parsed = parseInt(inputValue, 10);
    if (!isNaN(parsed) && parsed >= min && parsed <= max) {
      onChange(parsed);
    } else {
      setInputValue(String(value));
    }
    setEditing(false);
  };

  if (!editing) {
    return (
      <button
        onClick={() => setEditing(true)}
        className="w-8 rounded border border-transparent px-1 py-0.5 text-center text-xs font-medium text-gray-900 hover:border-gray-300 dark:text-gray-100 dark:hover:border-gray-600"
        aria-label={`Quantity: ${value}. Click to edit.`}
      >
        {value}
      </button>
    );
  }

  return (
    <input
      ref={inputRef}
      type="number"
      value={inputValue}
      onChange={(e) => setInputValue(e.target.value)}
      onBlur={commit}
      onKeyDown={(e) => {
        if (e.key === 'Enter') commit();
        if (e.key === 'Escape') {
          setInputValue(String(value));
          setEditing(false);
        }
      }}
      min={min}
      max={max}
      className="w-10 rounded border border-primary bg-white px-1 py-0.5 text-center text-xs font-medium text-gray-900 outline-none ring-1 ring-primary dark:bg-gray-800 dark:text-gray-100"
      aria-label="Edit quantity"
    />
  );
}
