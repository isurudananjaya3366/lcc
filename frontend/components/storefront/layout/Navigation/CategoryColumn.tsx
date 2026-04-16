'use client';

import React, { type FC } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import type { CategoryColumnProps } from './types/navigation';

const CategoryColumn: FC<CategoryColumnProps> = ({ category, className }) => {
  return (
    <div className={cn('space-y-3', className)}>
      {/* Category title */}
      <Link
        href={`/categories/${category.slug}`}
        className="block text-sm font-semibold text-gray-900 dark:text-gray-100 hover:text-green-700 dark:hover:text-green-400 transition-colors"
      >
        {category.name}
      </Link>

      {/* Subcategory links */}
      <ul className="space-y-2">
        {category.children.map((sub) => (
          <li key={sub.id}>
            <Link
              href={`/categories/${category.slug}/${sub.slug}`}
              className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:underline transition-colors duration-150"
            >
              {sub.name}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default CategoryColumn;
