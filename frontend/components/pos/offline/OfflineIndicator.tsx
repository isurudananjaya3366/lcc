// ================================================================
// OfflineIndicator + ConnectionStatusIcon — Tasks 73-74
// ================================================================

'use client';

import React from 'react';
import {
  useOfflineStatus,
  type ConnectionStatusType,
} from '@/hooks/useOfflineStatus';

// ----------------------------------------------------------------
// Status config map
// ----------------------------------------------------------------

interface StatusConfig {
  icon: string;
  color: string;
  textColor: string;
  bgColor: string;
  text: string;
  animation?: string;
}

const STATUS_CONFIG: Record<ConnectionStatusType, StatusConfig> = {
  ONLINE: {
    icon: '✓',
    color: 'text-green-600',
    textColor: 'text-green-700 dark:text-green-400',
    bgColor: 'bg-green-50 dark:bg-green-900/30',
    text: 'Online',
  },
  OFFLINE: {
    icon: '✗',
    color: 'text-red-600',
    textColor: 'text-red-700 dark:text-red-400',
    bgColor: 'bg-red-50 dark:bg-red-900/30',
    text: 'Offline',
  },
  SYNCING: {
    icon: '⟳',
    color: 'text-amber-600',
    textColor: 'text-amber-700 dark:text-amber-400',
    bgColor: 'bg-amber-50 dark:bg-amber-900/30',
    text: 'Syncing...',
    animation: 'animate-spin',
  },
  SYNC_ERROR: {
    icon: '⚠',
    color: 'text-orange-600',
    textColor: 'text-orange-700 dark:text-orange-400',
    bgColor: 'bg-orange-50 dark:bg-orange-900/30',
    text: 'Sync Error',
  },
};

const ICON_SIZE = {
  small: 'w-4 h-4 text-xs',
  medium: 'w-6 h-6 text-sm',
  large: 'w-8 h-8 text-base',
} as const;

// ----------------------------------------------------------------
// ConnectionStatusIcon
// ----------------------------------------------------------------

interface ConnectionStatusIconProps {
  status: ConnectionStatusType;
  size?: 'small' | 'medium' | 'large';
  className?: string;
  showAnimation?: boolean;
}

export function ConnectionStatusIcon({
  status,
  size = 'medium',
  className = '',
  showAnimation = true,
}: ConnectionStatusIconProps) {
  const cfg = STATUS_CONFIG[status];
  return (
    <span
      className={`inline-flex items-center justify-center ${ICON_SIZE[size]} ${cfg.color} ${showAnimation && cfg.animation ? cfg.animation : ''} ${className}`}
      aria-hidden="true"
    >
      {cfg.icon}
    </span>
  );
}

// ----------------------------------------------------------------
// OfflineIndicator
// ----------------------------------------------------------------

interface OfflineIndicatorProps {
  className?: string;
  showText?: boolean;
  compact?: boolean;
  status?: ConnectionStatusType;
  lastSyncTime?: Date | null;
}

export function OfflineIndicator({
  className = '',
  showText = true,
  compact = false,
  status: statusOverride,
  lastSyncTime: lstOverride,
}: OfflineIndicatorProps) {
  const live = useOfflineStatus();
  const status = statusOverride ?? live.status;
  const lastSyncTime = lstOverride ?? live.lastSyncTime;
  const cfg = STATUS_CONFIG[status];

  const timeFmt = lastSyncTime
    ? `Last sync: ${lastSyncTime.toLocaleTimeString()}`
    : null;

  const tooltipText = `Status: ${cfg.text}${timeFmt ? ` | ${timeFmt}` : ''}`;

  return (
    <div
      className={`flex items-center gap-2 rounded-lg transition-all hover:bg-opacity-75 ${compact ? 'px-1 py-1' : 'px-3 py-2'} ${cfg.bgColor} ${className}`}
      role="status"
      aria-label={`Connection status: ${cfg.text}`}
      aria-live="polite"
      aria-atomic="true"
      tabIndex={0}
      title={tooltipText}
    >
      <ConnectionStatusIcon
        status={status}
        size={compact ? 'small' : 'medium'}
      />
      {showText && !compact && (
        <div className="flex flex-col">
          <span
            className={`text-sm font-medium ${cfg.textColor} hidden sm:inline`}
          >
            {cfg.text}
          </span>
          {timeFmt && (
            <span className="text-xs text-gray-500 dark:text-gray-400 hidden md:inline">
              {timeFmt}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
