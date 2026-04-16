'use client';

import React, { useState, type FC } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

interface MobileNavItemData {
  id: string;
  label: string;
  href: string;
  children?: MobileNavItemData[];
}

interface MobileNavItemProps {
  item: MobileNavItemData;
  isSubmenuOpen: boolean;
  onToggleSubmenu: (id: string) => void;
  onClose: () => void;
}

const MobileNavItem: FC<MobileNavItemProps> = ({
  item,
  isSubmenuOpen,
  onToggleSubmenu,
  onClose,
}) => {
  const pathname = usePathname();
  const hasChildren = item.children && item.children.length > 0;
  const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);

  return (
    <li>
      <div className="flex items-center">
        <Link
          href={item.href}
          onClick={onClose}
          className={cn(
            'flex-1 flex items-center min-h-[48px] px-4 py-3 text-sm transition-colors',
            isActive
              ? 'bg-gray-100 dark:bg-gray-800 text-green-700 dark:text-green-400 font-semibold'
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800'
          )}
          aria-current={isActive ? 'page' : undefined}
        >
          {item.label}
        </Link>

        {hasChildren && (
          <button
            type="button"
            onClick={() => onToggleSubmenu(item.id)}
            className="flex items-center justify-center w-12 min-h-[48px] text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            aria-expanded={isSubmenuOpen}
            aria-label={`${isSubmenuOpen ? 'Collapse' : 'Expand'} ${item.label} submenu`}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className={cn(
                'h-4 w-4 transition-transform duration-200',
                isSubmenuOpen && 'rotate-90'
              )}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        )}
      </div>

      {/* Submenu */}
      {hasChildren && isSubmenuOpen && (
        <ul className="bg-gray-50 dark:bg-gray-800/50">
          {item.children!.map((child) => (
            <li key={child.id}>
              <Link
                href={child.href}
                onClick={onClose}
                className={cn(
                  'flex items-center min-h-[48px] pl-10 pr-4 py-3 text-sm transition-colors',
                  pathname === child.href
                    ? 'text-green-700 dark:text-green-400 font-medium bg-green-50 dark:bg-green-900/20'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-700'
                )}
                aria-current={pathname === child.href ? 'page' : undefined}
              >
                {child.label}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </li>
  );
};

export default MobileNavItem;
