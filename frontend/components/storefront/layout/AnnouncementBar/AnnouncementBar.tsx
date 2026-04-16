'use client';

import React, { useState, type FC } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import type { AnnouncementBarConfig } from '@/types/store/layout';
import LayoutContainer from '../LayoutContainer';

export interface AnnouncementBarProps {
  config: AnnouncementBarConfig;
  onDismiss?: () => void;
  className?: string;
}

const AnnouncementBar: FC<AnnouncementBarProps> = ({ config, onDismiss, className }) => {
  const [isVisible, setIsVisible] = useState(true);

  if (!config.enabled || !isVisible) {
    return null;
  }

  const handleDismiss = () => {
    setIsVisible(false);
    onDismiss?.();
  };

  return (
    <div
      role="banner"
      className={cn(
        config.backgroundColor,
        config.textColor,
        'py-2 transition-all duration-300',
        className
      )}
    >
      <LayoutContainer>
        <div className="flex items-center justify-center gap-2 text-sm font-medium">
          {/* Optional icon */}
          {config.icon && <span className="shrink-0">{config.icon}</span>}

          {/* Message */}
          <p className="truncate">{config.message}</p>

          {/* Optional CTA link */}
          {config.link && config.linkText && (
            <Link
              href={config.link}
              className="shrink-0 underline underline-offset-2 hover:opacity-80 transition-opacity font-semibold"
            >
              {config.linkText}
            </Link>
          )}

          {/* Dismiss button */}
          <button
            type="button"
            onClick={handleDismiss}
            className="ml-4 shrink-0 p-0.5 rounded hover:opacity-70 transition-opacity"
            aria-label="Dismiss announcement"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </LayoutContainer>
    </div>
  );
};

export default AnnouncementBar;
