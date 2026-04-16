'use client';

import React, { useState, type FC } from 'react';
import { cn } from '@/lib/utils';
import MobileNavItem from './MobileNavItem';

interface MobileNavItemData {
  id: string;
  label: string;
  href: string;
  children?: MobileNavItemData[];
}

interface MobileNavListProps {
  items?: MobileNavItemData[];
  onClose: () => void;
  className?: string;
}

const defaultNavItems: MobileNavItemData[] = [
  { id: 'home', label: 'Home', href: '/' },
  { id: 'shop', label: 'Shop', href: '/shop' },
  {
    id: 'categories',
    label: 'Categories',
    href: '/categories',
    children: [
      { id: 'electronics', label: 'Electronics', href: '/categories/electronics' },
      { id: 'clothing', label: 'Clothing', href: '/categories/clothing' },
      { id: 'home-living', label: 'Home & Living', href: '/categories/home-living' },
    ],
  },
  { id: 'deals', label: 'Deals', href: '/deals' },
  { id: 'new', label: 'New Arrivals', href: '/new-arrivals' },
];

const MobileNavList: FC<MobileNavListProps> = ({ items, onClose, className }) => {
  const [openSubmenuId, setOpenSubmenuId] = useState<string | null>(null);
  const navItems = items ?? defaultNavItems;

  const handleToggleSubmenu = (id: string) => {
    setOpenSubmenuId((prev) => (prev === id ? null : id));
  };

  return (
    <nav className={cn('w-full py-2', className)} aria-label="Mobile navigation">
      <ul className="list-none space-y-0.5">
        {navItems.map((item) => (
          <MobileNavItem
            key={item.id}
            item={item}
            isSubmenuOpen={openSubmenuId === item.id}
            onToggleSubmenu={handleToggleSubmenu}
            onClose={onClose}
          />
        ))}
      </ul>
    </nav>
  );
};

export default MobileNavList;
