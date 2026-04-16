'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import { useStoreUIStore } from '@/stores/store/ui';
import HamburgerIcon from './HamburgerIcon';

const MobileMenuButton: FC<{ className?: string }> = ({ className }) => {
  const mobileMenuOpen = useStoreUIStore((s) => s.mobileMenuOpen);
  const toggleMobileMenu = useStoreUIStore((s) => s.toggleMobileMenu);

  return (
    <button
      type="button"
      onClick={toggleMobileMenu}
      className={cn(
        'inline-flex items-center justify-center p-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors md:hidden',
        className
      )}
      aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
      aria-expanded={mobileMenuOpen}
      aria-controls="mobile-nav-drawer"
    >
      <HamburgerIcon isOpen={mobileMenuOpen} />
    </button>
  );
};

export default MobileMenuButton;
