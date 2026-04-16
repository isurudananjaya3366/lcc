'use client';

import React, { useEffect, useRef, useCallback, type FC } from 'react';
import { cn } from '@/lib/utils';
import { useStoreUIStore } from '@/stores/store/ui';
import DrawerBackdrop from './DrawerBackdrop';
import DrawerHeader from './DrawerHeader';
import MobileSearch from './MobileSearch';
import MobileNavList from './MobileNavList';
import MobileAccountLinks from './MobileAccountLinks';
import MobileContactInfo from './MobileContactInfo';

const MobileDrawer: FC = () => {
  const isOpen = useStoreUIStore((s) => s.mobileMenuOpen);
  const setMobileMenuOpen = useStoreUIStore((s) => s.setMobileMenuOpen);
  const drawerRef = useRef<HTMLDivElement>(null);

  const handleClose = () => setMobileMenuOpen(false);

  // Focus trap
  const handleFocusTrap = useCallback((e: KeyboardEvent) => {
    if (e.key !== 'Tab' || !drawerRef.current) return;
    const focusableEls = drawerRef.current.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    if (focusableEls.length === 0) return;
    const first = focusableEls[0];
    const last = focusableEls[focusableEls.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }, []);

  // Lock body scroll, handle Escape key, and focus trap
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';

      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') handleClose();
        handleFocusTrap(e);
      };
      document.addEventListener('keydown', handleKeyDown);

      // Focus first focusable element
      requestAnimationFrame(() => {
        const firstFocusable = drawerRef.current?.querySelector<HTMLElement>(
          'a[href], button:not([disabled]), input:not([disabled])'
        );
        firstFocusable?.focus();
      });

      return () => {
        document.body.style.overflow = '';
        document.removeEventListener('keydown', handleKeyDown);
      };
    } else {
      document.body.style.overflow = '';
    }
  }, [isOpen, handleFocusTrap]);

  if (!isOpen) return null;

  return (
    <div className="lg:hidden">
      {/* Backdrop */}
      <DrawerBackdrop onClose={handleClose} />

      {/* Drawer panel */}
      <div
        ref={drawerRef}
        id="mobile-nav-drawer"
        className={cn(
          'fixed top-0 left-0 bottom-0 z-50 w-[80vw] max-w-[320px] bg-white dark:bg-gray-900 shadow-xl flex flex-col',
          'animate-in slide-in-from-left duration-300'
        )}
        role="dialog"
        aria-label="Mobile navigation"
        aria-modal="true"
      >
        {/* Header with logo and close button */}
        <DrawerHeader onClose={handleClose} />

        {/* Search */}
        <MobileSearch onClose={handleClose} />

        {/* Scrollable content */}
        <div className="flex-1 overflow-y-auto">
          {/* Navigation list */}
          <MobileNavList onClose={handleClose} />

          {/* Account links */}
          <MobileAccountLinks onClose={handleClose} />

          {/* Contact info */}
          <MobileContactInfo />
        </div>
      </div>
    </div>
  );
};

export default MobileDrawer;
