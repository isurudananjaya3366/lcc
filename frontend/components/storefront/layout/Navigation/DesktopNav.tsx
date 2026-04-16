'use client';

import React, { type FC } from 'react';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import type { DesktopNavProps, NavigationItem } from './types/navigation';
import NavItem from './NavItem';

function isNavItemActive(pathname: string, navHref: string): boolean {
  if (navHref === '/') return pathname === '/';
  return pathname === navHref || pathname.startsWith(`${navHref}/`);
}

const defaultNavItems: NavigationItem[] = [
  { id: 'home', name: 'Home', href: '/' },
  { id: 'shop', name: 'Shop', href: '/shop' },
  { id: 'categories', name: 'Categories', href: '/categories', children: [] },
  { id: 'deals', name: 'Deals', href: '/deals' },
  { id: 'new', name: 'New Arrivals', href: '/new-arrivals' },
];

const DesktopNav: FC<DesktopNavProps> = ({ items, className }) => {
  const pathname = usePathname();
  const navItems = items ?? defaultNavItems;

  return (
    <nav
      className={cn(
        'hidden md:flex items-center bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-4 lg:px-6 h-14 z-40',
        className
      )}
      aria-label="Main navigation"
    >
      <div className="flex items-center gap-6 max-w-7xl mx-auto w-full">
        {navItems.map((item) => (
          <NavItem
            key={item.id}
            item={item}
            isActive={isNavItemActive(pathname, item.href)}
            hasMegaMenu={!!item.children && item.children.length > 0}
          />
        ))}
      </div>
    </nav>
  );
};

export default DesktopNav;
