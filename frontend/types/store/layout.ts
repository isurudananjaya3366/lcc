import type { ReactNode } from 'react';

// ─── Store Layout Props ────────────────────────────────────────────────────

export interface StoreLayoutProps {
  children: ReactNode;
  className?: string;
  showAnnouncementBar?: boolean;
}

// ─── Announcement Bar ──────────────────────────────────────────────────────

export interface AnnouncementBarConfig {
  enabled: boolean;
  message: string;
  link?: string;
  linkText?: string;
  backgroundColor: string;
  textColor: string;
  icon?: ReactNode;
}

export interface AnnouncementBarState {
  isDismissed: boolean;
  dismissedAt: number | null;
  dismiss: () => void;
  reset: () => void;
  shouldShow: (expiryDays?: number) => boolean;
}

// ─── Layout Scroll ─────────────────────────────────────────────────────────

export interface LayoutScrollState {
  scrollY: number;
  scrollDirection: 'up' | 'down' | 'none';
  isScrolled: boolean;
  threshold: number;
}

export type HeaderBehavior = 'always-visible' | 'hide-on-scroll-down' | 'sticky';

// ─── Layout Animation ─────────────────────────────────────────────────────

export interface LayoutAnimation {
  enabled: boolean;
  enterAnimation: string;
  exitAnimation: string;
  duration: number;
}

// ─── Utility Types ─────────────────────────────────────────────────────────

export type LayoutSection = 'header' | 'main' | 'footer' | 'announcement';

export interface LayoutTheme {
  backgroundColor: string;
  headerBackground: string;
  footerBackground: string;
  announcementBackground: string;
  textColor: string;
}

// ─── Container Props ───────────────────────────────────────────────────────

export type ContainerMaxWidth = 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';

export interface LayoutContainerProps {
  children: ReactNode;
  className?: string;
  maxWidth?: ContainerMaxWidth;
  padding?: boolean;
}

// ─── Main Content Props ────────────────────────────────────────────────────

export interface MainContentProps {
  children: ReactNode;
  className?: string;
  useContainer?: boolean;
  backgroundColor?: string;
}

// ─── Sticky Header ─────────────────────────────────────────────────────────

export interface UseStickyHeaderOptions {
  behavior?: HeaderBehavior;
  threshold?: number;
}

export interface StickyHeaderState {
  isSticky: boolean;
  isVisible: boolean;
  shouldAnimate: boolean;
  headerOffset: number;
}

// ─── Scroll Position Hook ──────────────────────────────────────────────────

export interface ScrollPosition {
  scrollY: number;
  scrollX: number;
  scrollDirection: 'up' | 'down' | 'none';
  isScrolled: boolean;
}

export interface UseScrollPositionOptions {
  threshold?: number;
}
