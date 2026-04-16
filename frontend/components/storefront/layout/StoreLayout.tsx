'use client';

import React, { type ReactNode, type FC } from 'react';
import { cn } from '@/lib/utils';
import SkipToContent from './SkipToContent';
import { AnnouncementBar } from './AnnouncementBar';
import MainContent from './MainContent';
import LayoutAnimationWrapper from './LayoutAnimationWrapper';
import { Header } from './Header';
import { Footer } from './Footer';
import { FloatingContainer } from './Floating';
import { CookieConsent } from './Floating';
import { defaultAnnouncementConfig } from '@/config/store/announcementBar.config';
import { useAnnouncementStore } from '@/stores/store/announcement';
import type { AnnouncementBarConfig } from '@/types/store/layout';

export interface StoreLayoutProps {
  children: ReactNode;
  className?: string;
  showAnnouncementBar?: boolean;
  hideHeader?: boolean;
  hideFooter?: boolean;
  fullWidth?: boolean;
  announcementConfig?: AnnouncementBarConfig;
}

/**
 * Main store layout component — wraps all storefront pages.
 * Five-section structure: skip link, announcement bar, header, main content, footer.
 */
const StoreLayout: FC<StoreLayoutProps> = ({
  children,
  className,
  showAnnouncementBar = true,
  hideHeader = false,
  hideFooter = false,
  fullWidth = false,
  announcementConfig = defaultAnnouncementConfig,
}) => {
  const { shouldShow, dismiss } = useAnnouncementStore();
  const displayAnnouncement = showAnnouncementBar && shouldShow();

  return (
    <div className={cn('min-h-screen flex flex-col bg-gray-50', className)}>
      {/* Skip navigation for accessibility */}
      <SkipToContent />

      {/* Announcement bar */}
      {displayAnnouncement && (
        <AnnouncementBar config={announcementConfig} onDismiss={dismiss} />
      )}

      {/* Header */}
      {!hideHeader && <Header />}

      {/* Main content with animation */}
      <LayoutAnimationWrapper>
        <MainContent useContainer={!fullWidth}>{children}</MainContent>
      </LayoutAnimationWrapper>

      {/* Footer */}
      {!hideFooter && <Footer />}

      {/* Floating elements */}
      <FloatingContainer whatsappNumber="0771234567" />
      <CookieConsent />
    </div>
  );
};

export default StoreLayout;
