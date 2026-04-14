'use client';

import { useCallback, useEffect, useMemo, useState, useSyncExternalStore } from 'react';
import { useUIStore } from '@/stores/useUIStore';

// ─── useMediaQuery ──────────────────────────────────────────────

/**
 * Subscribe to a CSS media query and return whether it currently matches.
 */
export function useMediaQuery(query: string): boolean {
  const subscribe = useCallback(
    (callback: () => void) => {
      const mql = window.matchMedia(query);
      mql.addEventListener('change', callback);
      return () => mql.removeEventListener('change', callback);
    },
    [query]
  );

  const getSnapshot = useCallback(() => window.matchMedia(query).matches, [query]);
  const getServerSnapshot = useCallback(() => false, []);

  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}

// ─── useSidebarState ────────────────────────────────────────────

export interface SidebarState {
  isCollapsed: boolean;
  isMobileOpen: boolean;
  toggle: () => void;
  open: () => void;
  close: () => void;
}

/**
 * Provides sidebar open/collapsed state plus mobile overlay control.
 * On screens < 1024px the sidebar is hidden by default and opens as an overlay.
 */
export function useSidebarState(): SidebarState {
  const isCollapsed = useUIStore((s) => s.isCollapsed);
  const toggleSidebar = useUIStore((s) => s.toggleSidebar);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const isMobile = useMediaQuery('(max-width: 1023px)');

  // Close mobile overlay when resizing to desktop
  useEffect(() => {
    if (!isMobile) setIsMobileOpen(false);
  }, [isMobile]);

  const toggle = useCallback(() => {
    if (isMobile) {
      setIsMobileOpen((prev) => !prev);
    } else {
      toggleSidebar();
    }
  }, [isMobile, toggleSidebar]);

  const open = useCallback(() => {
    if (isMobile) setIsMobileOpen(true);
  }, [isMobile]);

  const close = useCallback(() => {
    if (isMobile) setIsMobileOpen(false);
  }, [isMobile]);

  return { isCollapsed, isMobileOpen, toggle, open, close };
}

// ─── useLayoutDimensions ────────────────────────────────────────

export interface LayoutDimensions {
  sidebarWidth: number;
  headerHeight: number;
  contentPadding: number;
  contentWidth: number;
  contentHeight: number;
}

/**
 * Returns computed layout dimensions based on the current sidebar state
 * and viewport size.
 */
export function useLayoutDimensions(): LayoutDimensions {
  const isCollapsed = useUIStore((s) => s.isCollapsed);
  const isMobile = useMediaQuery('(max-width: 1023px)');

  const [viewport, setViewport] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const update = () => setViewport({ width: window.innerWidth, height: window.innerHeight });
    update();
    window.addEventListener('resize', update);
    return () => window.removeEventListener('resize', update);
  }, []);

  return useMemo(() => {
    const sidebarWidth = isMobile ? 0 : isCollapsed ? 64 : 240;
    const headerHeight = 64;
    const contentPadding = isMobile ? 16 : 24;
    const contentWidth = viewport.width - sidebarWidth;
    const contentHeight = viewport.height - headerHeight;

    return { sidebarWidth, headerHeight, contentPadding, contentWidth, contentHeight };
  }, [isCollapsed, isMobile, viewport]);
}

// ─── useLayout (combined convenience hook) ──────────────────────

export interface LayoutState extends LayoutDimensions {
  sidebar: SidebarState;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
}

/**
 * Combined convenience hook exposing all layout state in a single call.
 */
export function useLayout(): LayoutState {
  const sidebar = useSidebarState();
  const dimensions = useLayoutDimensions();
  const isMobile = useMediaQuery('(max-width: 639px)');
  const isTablet = useMediaQuery('(min-width: 640px) and (max-width: 1023px)');
  const isDesktop = useMediaQuery('(min-width: 1024px)');

  return { ...dimensions, sidebar, isMobile, isTablet, isDesktop };
}
