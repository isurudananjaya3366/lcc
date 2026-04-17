'use client';

import React, { useState, type FC } from 'react';
import { cn } from '@/lib/utils';

interface CouponInputProps {
  onApply: (code: string) => void;
  isLoading: boolean;
  className?: string;
}

const CouponInput: FC<CouponInputProps> = ({ onApply, isLoading, className }) => {
  const [code, setCode] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = code.trim();
    if (!trimmed) return;
    onApply(trimmed.toUpperCase());
  };

  return (
    <form onSubmit={handleSubmit} className={cn('flex gap-2', className)}>
      <input
        type="text"
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="Enter coupon code"
        className={cn(
          'flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm',
          'placeholder:text-gray-400',
          'focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500',
          'dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 dark:placeholder:text-gray-500',
          'dark:focus:border-green-400 dark:focus:ring-green-400'
        )}
        disabled={isLoading}
      />
      <button
        type="submit"
        disabled={!code.trim() || isLoading}
        className={cn(
          'rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white',
          'hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2',
          'disabled:cursor-not-allowed disabled:opacity-50',
          'dark:bg-green-500 dark:hover:bg-green-600 dark:focus:ring-offset-gray-900'
        )}
      >
        {isLoading ? 'Applying…' : 'Apply'}
      </button>
    </form>
  );
};

export default CouponInput;
