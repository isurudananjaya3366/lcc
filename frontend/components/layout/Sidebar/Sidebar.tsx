'use client';

import { useCallback, useEffect, useMemo } from 'react';
import { useUIStore } from '@/stores/useUIStore';
import { useAuthStore } from '@/stores/useAuthStore';
import { navigationMenuItems } from '@/config/navigation-menu';
import { filterMenuByPermissions } from '@/lib/navigation';
import { cn } from '@/lib/cn';
import { TooltipProvider } from '@/components/ui/tooltip';
import { SidebarHeader } from './SidebarHeader';
import { SidebarNav } from './SidebarNav';
import { SidebarFooter } from './SidebarFooter';

export function Sidebar() {
  const isCollapsed = useUIStore((s) => s.isCollapsed);
  const toggleSidebar = useUIStore((s) => s.toggleSidebar);
  const hasPermission = useAuthStore((s) => s.hasPermission);

  // Filter menu items by user permissions
  const visibleItems = useMemo(
    () => filterMenuByPermissions(navigationMenuItems, hasPermission),
    [hasPermission]
  );

  // Global keyboard shortcut: Ctrl/Cmd + B to toggle sidebar
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        toggleSidebar();
      }
    },
    [toggleSidebar]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return (
    <TooltipProvider delayDuration={200}>
      <aside
        className={cn(
          'flex h-full flex-col overflow-y-auto overflow-x-hidden bg-slate-900 text-gray-100 transition-all duration-300 ease-in-out',
          'border-r border-slate-700',
          'motion-reduce:transition-none',
          'print:hidden'
        )}
        role="navigation"
        aria-label="Main navigation"
        aria-expanded={!isCollapsed}
      >
        <SidebarHeader isCollapsed={isCollapsed} onToggle={toggleSidebar} />
        <SidebarNav items={visibleItems} isCollapsed={isCollapsed} />
        <SidebarFooter isCollapsed={isCollapsed} />
      </aside>
    </TooltipProvider>
  );
}
