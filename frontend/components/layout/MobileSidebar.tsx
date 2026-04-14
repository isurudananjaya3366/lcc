'use client';

import { useEffect } from 'react';
import { X } from 'lucide-react';
import { cn } from '@/lib/cn';
import { SidebarHeader } from './Sidebar/SidebarHeader';
import { SidebarNav } from './Sidebar/SidebarNav';
import { SidebarFooter } from './Sidebar/SidebarFooter';
import { useSwipeGesture } from '@/hooks/useSwipeGesture';
import { useIsMobile } from '@/hooks/useBreakpoint';
import { useUIStore } from '@/stores/useUIStore';
import { useAuthStore } from '@/stores/useAuthStore';
import { navigationMenuItems } from '@/config/navigation-menu';
import { filterMenuByPermissions } from '@/lib/navigation';
import { TooltipProvider } from '@/components/ui/tooltip';
import { useMemo } from 'react';

interface MobileSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function MobileSidebar({ isOpen, onClose }: MobileSidebarProps) {
  const isMobile = useIsMobile();
  const isCollapsed = useUIStore((s) => s.isCollapsed);
  const toggleSidebar = useUIStore((s) => s.toggleSidebar);
  const hasPermission = useAuthStore((s) => s.hasPermission);

  const visibleItems = useMemo(
    () => filterMenuByPermissions(navigationMenuItems, hasPermission),
    [hasPermission]
  );

  // Swipe left on drawer to close
  const { onTouchStart, onTouchMove, onTouchEnd } = useSwipeGesture(
    { onSwipeLeft: onClose },
    { threshold: 50, velocityThreshold: 0.3 }
  );

  // Lock body scroll when open
  useEffect(() => {
    if (isOpen && isMobile) {
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = '';
      };
    }
  }, [isOpen, isMobile]);

  // Close on Escape
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [isOpen, onClose]);

  if (!isMobile) return null;

  return (
    <TooltipProvider delayDuration={200}>
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex w-4/5 max-w-[320px] flex-col bg-slate-900 text-gray-100 shadow-2xl',
          'transition-transform duration-300 ease-in-out',
          'motion-reduce:transition-none',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
        role="dialog"
        aria-modal="true"
        aria-label="Mobile navigation"
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={onTouchEnd}
      >
        {/* Close button */}
        <div className="absolute right-2 top-3 z-10">
          <button
            type="button"
            onClick={onClose}
            className="flex h-10 w-10 items-center justify-center rounded-lg text-gray-400 transition-colors hover:bg-slate-800 hover:text-gray-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
            aria-label="Close navigation menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <SidebarHeader isCollapsed={false} onToggle={toggleSidebar} />
        <SidebarNav items={visibleItems} isCollapsed={false} />
        <SidebarFooter isCollapsed={false} />
      </aside>
    </TooltipProvider>
  );
}
