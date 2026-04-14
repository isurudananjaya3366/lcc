'use client';

import { cn } from '@/lib/cn';

interface SidebarOverlayProps {
  isVisible: boolean;
  onClose: () => void;
}

/**
 * Semi-transparent backdrop rendered behind the mobile sidebar drawer.
 * Click to close the drawer.
 */
export function SidebarOverlay({ isVisible, onClose }: SidebarOverlayProps) {
  return (
    <div
      className={cn(
        'fixed inset-0 z-40 bg-black/50 transition-opacity duration-300 ease-in-out lg:hidden',
        'motion-reduce:transition-none',
        isVisible ? 'opacity-100' : 'pointer-events-none opacity-0'
      )}
      onClick={onClose}
      aria-hidden="true"
    />
  );
}
