'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import type { MegaMenuPanelProps } from './types/navigation';
import MegaMenuCategories from './MegaMenuCategories';
import MegaMenuFeatured from './MegaMenuFeatured';

const MegaMenuPanel: FC<MegaMenuPanelProps> = ({ categories, featured, className }) => {
  return (
    <div
      className={cn(
        'bg-white dark:bg-gray-900 shadow-xl border border-gray-100 dark:border-gray-800 rounded-b-lg p-6',
        className
      )}
    >
      <div className="flex gap-6">
        {/* Categories section (75%) */}
        <MegaMenuCategories categories={categories} />

        {/* Featured section (25%) */}
        {featured && <MegaMenuFeatured featured={featured} />}
      </div>
    </div>
  );
};

export default MegaMenuPanel;
