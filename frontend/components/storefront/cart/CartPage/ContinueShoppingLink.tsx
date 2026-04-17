import React, { type FC } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';

interface ContinueShoppingLinkProps {
  className?: string;
}

const ContinueShoppingLink: FC<ContinueShoppingLinkProps> = ({ className }) => {
  return (
    <Link
      href="/products"
      className={cn(
        'inline-flex items-center gap-1 text-sm font-medium text-green-700 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300 transition-colors',
        className,
      )}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-4 w-4"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
      </svg>
      Continue Shopping
    </Link>
  );
};

export default ContinueShoppingLink;
