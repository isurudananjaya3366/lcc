'use client';

import { useState } from 'react';
import { toast } from 'sonner';

interface AddToCartButtonProps {
  onAdd: () => Promise<boolean> | boolean;
  disabled?: boolean;
}

export function AddToCartButton({ onAdd, disabled }: AddToCartButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const handleClick = async () => {
    if (isLoading || disabled) return;
    setIsLoading(true);
    try {
      const result = await onAdd();
      if (result) {
        setShowSuccess(true);
        toast.success('Added to cart!', {
          description: 'Item has been added to your cart.',
          action: {
            label: 'View Cart',
            onClick: () => { window.location.href = '/cart'; },
          },
          duration: 4000,
        });
        setTimeout(() => setShowSuccess(false), 2000);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled || isLoading}
      className={`
        flex w-full items-center justify-center gap-2 rounded-lg px-6 py-3 text-base font-semibold transition-all
        ${disabled
          ? 'cursor-not-allowed bg-gray-300 text-gray-500'
          : showSuccess
            ? 'bg-green-600 text-white'
            : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-[0.98]'
        }
      `}
    >
      {isLoading ? (
        <>
          <svg className="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Adding...
        </>
      ) : showSuccess ? (
        <>
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
          Added to Cart!
        </>
      ) : (
        <>
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 3h1.386c.51 0 .955.343 1.087.835l.383 1.437M7.5 14.25a3 3 0 00-3 3h15.75m-12.75-3h11.218c1.121 0 2.002-.881 2.002-2.003V6.75m-14.22 0h14.22" />
          </svg>
          Add to Cart
        </>
      )}
    </button>
  );
}
