import React, { type FC } from 'react';
import { cn } from '@/lib/utils';

interface EmptyCartIllustrationProps {
  className?: string;
}

const EmptyCartIllustration: FC<EmptyCartIllustrationProps> = ({ className }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 200 200"
      fill="none"
      className={cn('h-48 w-48 text-gray-300 dark:text-gray-600', className)}
      aria-hidden="true"
    >
      {/* Cart body */}
      <path
        d="M60 70h110l-14 50H74L60 70z"
        stroke="currentColor"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Cart handle */}
      <path
        d="M60 70l-8-30H30"
        stroke="currentColor"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Left wheel */}
      <circle
        cx="90"
        cy="140"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      {/* Right wheel */}
      <circle
        cx="140"
        cy="140"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      {/* Dashed line inside cart (empty indicator) */}
      <path
        d="M85 90h50M85 100h40M85 110h30"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeDasharray="4 4"
        opacity="0.5"
      />
    </svg>
  );
};

export default EmptyCartIllustration;
