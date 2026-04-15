'use client';

import React, { useState, type FC } from 'react';
import Link from 'next/link';

export interface NavigationItem {
  label: string;
  href: string;
  children?: NavigationItem[];
}

export interface StoreNavigationProps {
  items?: NavigationItem[];
  className?: string;
}

const defaultNavItems: NavigationItem[] = [
  { label: 'Home', href: '/' },
  {
    label: 'Shop',
    href: '/products',
    children: [
      { label: 'All Products', href: '/products' },
      { label: 'New Arrivals', href: '/search?sort=newest' },
      { label: 'Best Sellers', href: '/search?sort=popular' },
    ],
  },
  {
    label: 'Categories',
    href: '/search',
    children: [
      { label: 'Electronics', href: '/search?category=electronics' },
      { label: 'Fashion', href: '/search?category=fashion' },
      { label: 'Home & Garden', href: '/search?category=home' },
      { label: 'Health & Beauty', href: '/search?category=health' },
    ],
  },
  { label: 'Deals', href: '/search?category=deals' },
];

/**
 * Store navigation — primary navigation menu with dropdown support.
 * Used within StoreHeader. Supports desktop dropdowns and mobile accordion.
 */
const StoreNavigation: FC<StoreNavigationProps> = ({ items = defaultNavItems, className = '' }) => {
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);

  return (
    <nav aria-label="Store navigation" className={className}>
      <ul className="flex items-center gap-1">
        {items.map((item) => (
          <li
            key={item.label}
            className="relative"
            onMouseEnter={() => item.children && setOpenDropdown(item.label)}
            onMouseLeave={() => setOpenDropdown(null)}
          >
            <Link
              href={item.href}
              className="flex items-center gap-1 px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-green-700 dark:hover:text-green-400 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              {item.label}
              {item.children && (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className={`h-3.5 w-3.5 transition-transform ${openDropdown === item.label ? 'rotate-180' : ''}`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              )}
            </Link>

            {/* Dropdown */}
            {item.children && openDropdown === item.label && (
              <div className="absolute top-full left-0 mt-0 w-48 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg py-1 z-10">
                {item.children.map((child) => (
                  <Link
                    key={child.label}
                    href={child.href}
                    className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:text-green-700 dark:hover:text-green-400 transition-colors"
                  >
                    {child.label}
                  </Link>
                ))}
              </div>
            )}
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default StoreNavigation;
