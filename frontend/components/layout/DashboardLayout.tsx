'use client';

import type { ReactNode } from 'react';
import { useUIStore } from '@/stores/useUIStore';
import { useSidebarState } from '@/hooks/useLayout';
import { useSwipeGesture } from '@/hooks/useSwipeGesture';
import { MainContent } from './MainContent';
import { SkipNavigation } from './SkipNavigation';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { MobileSidebar } from './MobileSidebar';
import { SidebarOverlay } from './SidebarOverlay';
import { MobileBottomNav } from './MobileBottomNav';
import { cn } from '@/lib/cn';

/**
 * DashboardLayout — Primary dashboard grid structure.
 *
 * Implements CSS Grid with three areas:
 *   - Header: 64px fixed row spanning full width
 *   - Sidebar: left column (240px expanded, 64px collapsed) — hidden on mobile
 *   - Content: remaining space (scrollable)
 *
 * On mobile (<1024px) the sidebar is replaced by a slide-in drawer.
 */

interface DashboardLayoutProps {
  children: ReactNode;
  className?: string;
}

export function DashboardLayout({ children, className }: DashboardLayoutProps) {
  const isCollapsed = useUIStore((s) => s.isCollapsed);
  const { isMobileOpen, open, close } = useSidebarState();

  // Swipe right from left edge to open mobile drawer
  const { onTouchStart, onTouchMove, onTouchEnd } = useSwipeGesture(
    { onSwipeRight: open, onSwipeLeft: close },
    { threshold: 50, velocityThreshold: 0.3, edgeZone: 20, edgeOnly: true }
  );

  return (
    <>
      <SkipNavigation />

      <div
        className={cn(
          'grid h-screen w-full overflow-hidden',
          'grid-rows-[var(--header-height)_1fr]',
          'transition-[grid-template-columns] duration-300 ease-in-out',
          'motion-reduce:transition-none',
          // Desktop: sidebar column + content
          'lg:grid-cols-[var(--sidebar-width)_1fr]',
          isCollapsed && 'lg:grid-cols-[var(--sidebar-width-collapsed)_1fr]',
          // Mobile: no sidebar column
          'max-lg:grid-cols-[1fr]',
          className
        )}
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={onTouchEnd}
      >
        {/* Header — spans full width */}
        <Header />

        {/* Desktop Sidebar — hidden on mobile */}
        <div className="hidden lg:block">
          <Sidebar />
        </div>

        {/* Main Content */}
        <MainContent className="pb-16 md:pb-0">{children}</MainContent>
      </div>

      {/* Mobile sidebar overlay + drawer */}
      <SidebarOverlay isVisible={isMobileOpen} onClose={close} />
      <MobileSidebar isOpen={isMobileOpen} onClose={close} />

      {/* Mobile bottom navigation */}
      <MobileBottomNav />
    </>
  );
}
