// ================================================================
// OfflineRestrictions — Task 79
// ================================================================

'use client';

import React from 'react';
import { useFeatureRestriction } from '@/hooks/useFeatureRestriction';

type RestrictionType = 'DISABLED' | 'READ_ONLY' | 'QUEUED' | 'PARTIAL';

interface OfflineRestrictionsProps {
  children: React.ReactNode;
  type?: RestrictionType;
  feature: string;
  fallbackMessage?: string;
  showOverlay?: boolean;
  className?: string;
}

export function OfflineRestrictions({
  children,
  feature,
  fallbackMessage,
  showOverlay = true,
  className = '',
}: OfflineRestrictionsProps) {
  const { restriction, isRestricted } = useFeatureRestriction(feature);

  if (!isRestricted || !restriction) return <>{children}</>;

  const message = fallbackMessage ?? restriction.message;

  if (restriction.type === 'DISABLED' && showOverlay) {
    return (
      <div
        className={`relative ${className}`}
        aria-disabled="true"
        aria-label={`Feature disabled: ${message}`}
      >
        <div className="pointer-events-none opacity-40">{children}</div>
        <div className="absolute inset-0 bg-black/10 rounded flex items-center justify-center cursor-not-allowed">
          <span className="text-gray-500 dark:text-gray-400 text-sm bg-white dark:bg-gray-800 px-3 py-1 rounded shadow">
            {message}
          </span>
        </div>
      </div>
    );
  }

  if (restriction.type === 'READ_ONLY') {
    return (
      <div className={`${className}`}>
        <div className="pointer-events-none opacity-50">{children}</div>
        <span className="inline-block mt-1 px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs rounded">
          {message}
        </span>
      </div>
    );
  }

  if (restriction.type === 'QUEUED') {
    return (
      <div className={className}>
        {children}
        <span className="inline-flex items-center gap-1 mt-1 px-2 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 text-xs rounded">
          ⏱️ {message}
        </span>
      </div>
    );
  }

  // PARTIAL
  return (
    <div className={className}>
      {children}
      <span className="inline-block mt-1 px-2 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400 text-xs rounded">
        {message}
      </span>
    </div>
  );
}
