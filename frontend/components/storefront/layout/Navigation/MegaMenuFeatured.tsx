'use client';

import React, { type FC } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import type { MegaMenuFeaturedProps } from './types/navigation';
import FeaturedImage from './FeaturedImage';

const MegaMenuFeatured: FC<MegaMenuFeaturedProps> = ({ featured, className }) => {
  return (
    <div
      className={cn(
        'w-1/4 flex-shrink-0 bg-gray-50 dark:bg-gray-800 rounded-lg p-4 flex flex-col',
        className
      )}
    >
      <FeaturedImage src={featured.image} alt={featured.title} aspectRatio="4/3" />

      <div className="mt-3 space-y-1.5">
        <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">{featured.title}</h4>
        <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">
          {featured.description}
        </p>
        <Link
          href={featured.link}
          className="inline-block text-sm font-medium text-green-700 dark:text-green-400 hover:text-green-800 dark:hover:text-green-300 transition-colors mt-2"
        >
          {featured.ctaText}
        </Link>
      </div>
    </div>
  );
};

export default MegaMenuFeatured;
