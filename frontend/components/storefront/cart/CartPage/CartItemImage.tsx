'use client';

import React, { useState, type FC } from 'react';
import Image from 'next/image';
import { cn } from '@/lib/utils';

interface CartItemImageProps {
  src: string;
  alt: string;
  className?: string;
}

const CartItemImage: FC<CartItemImageProps> = ({ src, alt, className }) => {
  const [hasError, setHasError] = useState(false);

  return (
    <div
      className={cn(
        'relative h-20 w-20 flex-shrink-0 overflow-hidden rounded-lg border border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800',
        className,
      )}
    >
      {hasError || !src ? (
        <div className="flex h-full w-full items-center justify-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-8 w-8 text-gray-300 dark:text-gray-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>
      ) : (
        <Image
          src={src}
          alt={alt}
          fill
          sizes="80px"
          className="object-cover"
          onError={() => setHasError(true)}
        />
      )}
    </div>
  );
};

export default CartItemImage;
