'use client';

import React, { type FC } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import type { NavLinkProps } from './types/navigation';

const NavLink: FC<NavLinkProps> = ({ href, children, isActive = false, className }) => {
  return (
    <Link
      href={href}
      className={cn(
        'text-sm font-medium transition-colors duration-150 ease-in-out',
        'focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 rounded',
        isActive
          ? 'text-green-700 dark:text-green-400 font-semibold'
          : 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100',
        className
      )}
      aria-current={isActive ? 'page' : undefined}
    >
      {children}
    </Link>
  );
};

export default NavLink;
