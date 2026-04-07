// ================================================================
// useFeatureRestriction — Task 79
// ================================================================

'use client';

import { useMemo } from 'react';
import { useOfflineStatus } from '@/hooks/useOfflineStatus';

type RestrictionType =
  | 'DISABLED'
  | 'READ_ONLY'
  | 'QUEUED'
  | 'PARTIAL'
  | 'ENABLED';

interface FeatureRestriction {
  type: RestrictionType;
  message: string;
  alternatives?: string[];
}

const OFFLINE_RESTRICTIONS: Record<string, FeatureRestriction> = {
  reports: { type: 'DISABLED', message: 'Reports require online access' },
  settings: { type: 'READ_ONLY', message: 'Settings are read-only offline' },
  'user-management': {
    type: 'DISABLED',
    message: 'User management requires online',
  },
  'real-time-sync': {
    type: 'DISABLED',
    message: 'Real-time sync disabled offline',
  },
  'cloud-backup': {
    type: 'DISABLED',
    message: 'Cloud backup unavailable offline',
  },
  'card-payments': {
    type: 'QUEUED',
    message: 'Card payments queued for later',
  },
  'product-search': {
    type: 'PARTIAL',
    message: 'Search limited to cached products',
  },
  sales: { type: 'ENABLED', message: '' },
  'cash-payments': { type: 'ENABLED', message: '' },
  inventory: { type: 'QUEUED', message: 'Inventory updates queued for sync' },
};

export function useFeatureRestriction(feature: string) {
  const { isOnline } = useOfflineStatus();

  return useMemo(() => {
    if (isOnline) {
      return { restriction: null, isRestricted: false, canAccess: true };
    }
    const restriction = OFFLINE_RESTRICTIONS[feature] ?? null;
    const isRestricted = restriction !== null && restriction.type !== 'ENABLED';
    return { restriction, isRestricted, canAccess: !isRestricted };
  }, [isOnline, feature]);
}
