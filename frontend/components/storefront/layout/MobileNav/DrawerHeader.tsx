'use client';

import React, { type FC } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import CloseDrawerButton from './CloseDrawerButton';

interface DrawerHeaderProps {
  onClose: () => void;
  logoSrc?: string;
  className?: string;
}

const DrawerHeader: FC<DrawerHeaderProps> = ({ onClose, logoSrc, className }) => {
  return (
    <header
      className={cn(
        'flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0',
        className
      )}
    >
      <Link href="/" onClick={onClose} className="flex items-center gap-1">
        <span className="text-lg font-bold text-green-700 dark:text-green-400">Lanka</span>
        <span className="text-lg font-bold text-gray-800 dark:text-gray-200">Commerce</span>
      </Link>

      <CloseDrawerButton onClose={onClose} />
    </header>
  );
};

export default DrawerHeader;
