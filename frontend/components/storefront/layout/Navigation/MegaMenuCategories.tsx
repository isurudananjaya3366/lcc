'use client';

import React, { type FC } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import type { MegaMenuCategoriesProps } from './types/navigation';
import CategoryColumn from './CategoryColumn';

const MegaMenuCategories: FC<MegaMenuCategoriesProps> = ({ categories, className }) => {
  return (
    <div className={cn('flex-1', className)}>
      {/* Category columns grid */}
      <div className="grid grid-cols-3 gap-8">
        {categories.map((category) => (
          <CategoryColumn key={category.id} category={category} />
        ))}
      </div>

      {/* View All Categories link */}
      <div className="flex items-center justify-center pt-6 mt-6 border-t border-gray-200 dark:border-gray-700">
        <Link
          href="/categories"
          className="text-green-700 dark:text-green-400 font-medium hover:text-green-800 dark:hover:text-green-300 transition-colors flex items-center gap-2 group"
        >
          View All Categories
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-1"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M14 5l7 7m0 0l-7 7m7-7H3"
            />
          </svg>
        </Link>
      </div>
    </div>
  );
};

export default MegaMenuCategories;
