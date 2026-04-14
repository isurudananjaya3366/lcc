'use client';

import { useCallback, useEffect, useState } from 'react';
import { Menu, X } from 'lucide-react';
import { useSidebarState } from '@/hooks/useLayout';
import { cn } from '@/lib/cn';
import { GlobalSearch } from './GlobalSearch';
import { CommandPalette } from './CommandPalette';
import { NotificationBell } from './NotificationBell';
import { UserMenu } from './UserMenu';
import { ThemeToggle } from './ThemeToggle';
import { TenantSwitcher } from './TenantSwitcher';
import { HelpButton } from './HelpButton';
import { QuickActions } from './QuickActions';
import { HeaderLogo } from './HeaderLogo';

export function Header() {
  const { isMobileOpen, toggle } = useSidebarState();
  const [paletteOpen, setPaletteOpen] = useState(false);

  // Global keyboard shortcut for command palette
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setPaletteOpen(true);
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, []);

  const openPalette = useCallback(() => setPaletteOpen(true), []);

  return (
    <>
      <header
        className={cn(
          'flex items-center justify-between border-b bg-white px-4 shadow-sm lg:col-span-2 lg:px-6',
          'dark:border-gray-700 dark:bg-gray-800'
        )}
        style={{ zIndex: 'var(--z-header)' } as React.CSSProperties}
        role="banner"
      >
        {/* Left section */}
        <div className="flex items-center gap-2">
          {/* Mobile menu toggle */}
          <button
            type="button"
            onClick={toggle}
            className={cn(
              'flex h-10 w-10 items-center justify-center rounded-lg transition-colors lg:hidden',
              'hover:bg-gray-100 dark:hover:bg-gray-700',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary'
            )}
            aria-label={isMobileOpen ? 'Close navigation menu' : 'Open navigation menu'}
            aria-expanded={isMobileOpen}
            aria-controls="sidebar"
          >
            {isMobileOpen ? (
              <X className="h-5 w-5 text-gray-600 dark:text-gray-300" />
            ) : (
              <Menu className="h-5 w-5 text-gray-600 dark:text-gray-300" />
            )}
          </button>

          <HeaderLogo />
          <TenantSwitcher />
        </div>

        {/* Center — search */}
        <div className="flex flex-1 justify-center px-4">
          <GlobalSearch onOpenPalette={openPalette} />
        </div>

        {/* Right section */}
        <div className="flex items-center gap-1">
          <QuickActions />
          <HelpButton />
          <ThemeToggle />
          <NotificationBell />
          <UserMenu />
        </div>
      </header>

      <CommandPalette open={paletteOpen} onOpenChange={setPaletteOpen} />
    </>
  );
}
