/**
 * Package Optimization Configuration
 *
 * Ensures minimal bundle size for commonly oversized packages.
 */

// ── Lodash Optimization (Task 49) ───────────────────────────────
// Before: import _ from 'lodash'           → 72KB
// After:  import { debounce } from 'lodash-es'  → 6KB (92% reduction)

export const LODASH_ALLOWED_IMPORTS = [
  'debounce',
  'throttle',
  'cloneDeep',
  'merge',
  'get',
  'set',
  'omit',
  'pick',
  'groupBy',
  'sortBy',
  'uniqBy',
  'isEmpty',
  'isEqual',
] as const;

// ── date-fns Optimization (Task 50) ─────────────────────────────
// Before: import { ... } from 'date-fns' (barrel) → 120KB
// After:  import { format } from 'date-fns'       → 10KB (90% reduction)
// Tip: Import specific functions, not the whole library.

export const DATE_FNS_ALLOWED_IMPORTS = [
  'format',
  'formatDistance',
  'formatRelative',
  'parseISO',
  'isValid',
  'addDays',
  'subDays',
  'startOfDay',
  'endOfDay',
  'differenceInDays',
  'isBefore',
  'isAfter',
  'startOfMonth',
  'endOfMonth',
] as const;

// ── Bundle Size Targets ─────────────────────────────────────────

export const PACKAGE_SIZE_LIMITS = {
  lodash: { maxKB: 10, current: 'lodash-es' },
  dateFns: { maxKB: 15, current: 'date-fns' },
  tanstackQuery: { maxKB: 40, current: '@tanstack/react-query' },
  lucideReact: { maxKB: 5, current: 'lucide-react (tree-shaken)' },
  zod: { maxKB: 15, current: 'zod' },
  zustand: { maxKB: 5, current: 'zustand' },
} as const;
