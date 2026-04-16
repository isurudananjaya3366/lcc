'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import type { NavItemProps } from './types/navigation';
import { useHoverDelay } from './hooks';
import NavLink from './NavLink';
import SubmenuIndicator from './SubmenuIndicator';
import MegaMenu from './MegaMenu';
import MegaMenuPanel from './MegaMenuPanel';

const NavItem: FC<NavItemProps> = ({ item, isActive, hasMegaMenu, children }) => {
  const { isHovered, onMouseEnter, onMouseLeave } = useHoverDelay({
    openDelay: 100,
    closeDelay: 200,
  });

  return (
    <div
      className="relative"
      onMouseEnter={hasMegaMenu ? onMouseEnter : undefined}
      onMouseLeave={hasMegaMenu ? onMouseLeave : undefined}
    >
      <div className="flex items-center gap-1 py-4">
        <NavLink href={item.href} isActive={isActive}>
          {item.name}
        </NavLink>

        {hasMegaMenu && <SubmenuIndicator isOpen={isHovered} />}
      </div>

      {/* Mega menu */}
      {hasMegaMenu && item.children && (
        <MegaMenu isOpen={isHovered} onClose={onMouseLeave}>
          {children ?? <MegaMenuPanel categories={item.children} featured={item.featured} />}
        </MegaMenu>
      )}
    </div>
  );
};

export default NavItem;
