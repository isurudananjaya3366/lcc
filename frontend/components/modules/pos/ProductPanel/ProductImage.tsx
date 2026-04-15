'use client';

import Image from 'next/image';
import { Package } from 'lucide-react';
import { useState } from 'react';

interface ProductImageProps {
  src?: string | null;
  alt: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeMap = {
  sm: { container: 'h-10 w-10', px: 40 },
  md: { container: 'h-20 w-20', px: 80 },
  lg: { container: 'h-[120px] w-[120px]', px: 120 },
} as const;

export function ProductImage({ src, alt, size = 'md', className = '' }: ProductImageProps) {
  const [hasError, setHasError] = useState(false);
  const s = sizeMap[size];

  if (!src || hasError) {
    return (
      <div
        className={`${s.container} flex shrink-0 items-center justify-center rounded bg-gray-100 dark:bg-gray-700 ${className}`}
      >
        <Package className="h-1/2 w-1/2 text-gray-400" />
      </div>
    );
  }

  return (
    <div className={`${s.container} relative shrink-0 overflow-hidden rounded ${className}`}>
      <Image
        src={src}
        alt={alt}
        width={s.px}
        height={s.px}
        className="h-full w-full object-cover"
        loading="lazy"
        onError={() => setHasError(true)}
      />
    </div>
  );
}
