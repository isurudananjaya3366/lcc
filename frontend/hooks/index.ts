// ================================================================
// Custom React Hooks — Barrel Export
// ================================================================
// Reusable hooks for data fetching, state, UI, and SSR.
// Export hooks as they are created.
//
// Import: import { useDebounce, useLocalStorage } from '@/hooks'
// ================================================================

// Data hooks
// export { useDebounce } from './useDebounce'
// export { useAsync } from './useAsync'

// State hooks
// export { useLocalStorage } from './useLocalStorage'
// export { useToggle } from './useToggle'
// export { usePrevious } from './usePrevious'

// UI hooks
// export { useMediaQuery } from './useMediaQuery'
// export { useClickOutside } from './useClickOutside'
// export { useCopyToClipboard } from './useCopyToClipboard'

// SSR hooks
// export { useIsClient } from './useIsClient'
// export { useIsMounted } from './useIsMounted'

// Offline hooks
export { useCacheWarmup } from './useCacheWarmup';
export { useTransactionQueue } from './useTransactionQueue';
export { useOfflineStatus } from './useOfflineStatus';
export { useFeatureRestriction } from './useFeatureRestriction';
export { useSyncHistory } from './useSyncHistory';
export { useManualSync } from './useManualSync';
export { useSyncToasts } from './useSyncToasts';
export { useCacheRefresh } from './useCacheRefresh';
