'use client';

import React, { type FC } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import type { WishlistIconProps } from '@/types/store/header';

const WishlistIcon: FC<WishlistIconProps> = ({
  itemCount,
  isActive = false,
  onClick,
  href = '/account/wishlist',
  showBadge = true,
  className,
}) => {
  const content = (
    <>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className={cn('h-5 w-5', isActive && 'text-red-500')}
        fill={isActive ? 'currentColor' : 'none'}
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
        />
      </svg>
      {showBadge && itemCount > 0 && (
        <span
          className="absolute -top-1 -right-1 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-bold text-white bg-red-600 rounded-full border-2 border-white dark:border-gray-900"
          aria-hidden="true"
        >
          {itemCount > 99 ? '99+' : itemCount}
        </span>
      )}
    </>
  );

  const sharedClassNames = cn(
    'relative hidden lg:flex items-center p-2 text-gray-700 dark:text-gray-300 hover:text-green-700 dark:hover:text-green-400 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800',
    className
  );

  if (onClick) {
    return (
      <button
        type="button"
        onClick={onClick}
        className={sharedClassNames}
        aria-label={`Wishlist${itemCount > 0 ? `, ${itemCount} item${itemCount === 1 ? '' : 's'}` : ''}`}
      >
        {content}
      </button>
    );
  }

  return (
    <Link
      href={href}
      className={sharedClassNames}
      aria-label={`Wishlist${itemCount > 0 ? `, ${itemCount} item${itemCount === 1 ? '' : 's'}` : ''}`}
    >
      {content}
    </Link>
  );
};

export default WishlistIcon;
