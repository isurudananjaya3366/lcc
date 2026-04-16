'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import type { SubmenuIndicatorProps } from './types/navigation';

const SubmenuIndicator: FC<SubmenuIndicatorProps> = ({ isOpen, className }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={cn(
        'w-3.5 h-3.5 transition-transform duration-200',
        isOpen && 'rotate-180',
        className
      )}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
    </svg>
  );
};

export default SubmenuIndicator;
