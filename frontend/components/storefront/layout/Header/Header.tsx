'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import type { HeaderProps } from '@/types/store/header';
import { useStickyHeader } from '../hooks';
import HeaderContainer from './HeaderContainer';
import Logo from './Logo';
import HeaderSearch from './HeaderSearch';
import HeaderActions from './HeaderActions';

const Header: FC<HeaderProps> = ({ className, storeName = 'LankaCommerce' }) => {
  const { isSticky, isVisible, shouldAnimate } = useStickyHeader({
    behavior: 'hide-on-scroll-down',
    threshold: 80,
  });

  return (
    <header
      className={cn(
        'w-full bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 z-40',
        isSticky && 'fixed top-0 left-0 right-0 shadow-sm',
        isSticky && !isVisible && '-translate-y-full',
        shouldAnimate && 'transition-transform duration-300',
        className
      )}
    >
      <HeaderContainer>
        {/* Left: Logo */}
        <Logo alt={`${storeName} logo`} href="/" />

        {/* Center: Desktop search */}
        <HeaderSearch
          placeholder="Search products..."
          className="hidden md:flex flex-1 max-w-xl mx-4"
        />

        {/* Right: Actions */}
        <HeaderActions showSearch showWishlist />
      </HeaderContainer>
    </header>
  );
};

export default Header;
