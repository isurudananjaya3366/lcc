'use client';

import { useState, useEffect, useCallback } from 'react';
import type { PopupConfig } from '@/types/marketing/popup.types';
import { shouldShowPopup, recordPopupShown, recordPopupDismissed } from '@/lib/marketing/popupStorage';

export function usePopupTrigger(popup: PopupConfig | null) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (!popup || !shouldShowPopup(popup)) return;

    if (popup.trigger === 'page_load') {
      const timer = setTimeout(() => {
        setIsVisible(true);
        recordPopupShown(popup.id);
      }, popup.delayMs || 2000);
      return () => clearTimeout(timer);
    }

    if (popup.trigger === 'time_delay') {
      const timer = setTimeout(() => {
        setIsVisible(true);
        recordPopupShown(popup.id);
      }, popup.delayMs || 5000);
      return () => clearTimeout(timer);
    }

    if (popup.trigger === 'scroll' && popup.scrollPercentage) {
      const handler = () => {
        const scrolled = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
        if (scrolled >= (popup.scrollPercentage || 50)) {
          setIsVisible(true);
          recordPopupShown(popup.id);
          window.removeEventListener('scroll', handler);
        }
      };
      window.addEventListener('scroll', handler, { passive: true });
      return () => window.removeEventListener('scroll', handler);
    }
  }, [popup]);

  const dismiss = useCallback(() => {
    if (popup) recordPopupDismissed(popup.id);
    setIsVisible(false);
  }, [popup]);

  return { isVisible, dismiss };
}
