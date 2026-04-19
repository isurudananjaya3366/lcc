/**
 * Module Alias Optimization
 *
 * tsconfig.json paths (already configured as @/*) ensure clean imports
 * and help bundlers resolve modules efficiently.
 *
 * Additional optimization mappings for smaller bundle sizes.
 */

export const MODULE_REPLACEMENTS = {
  /** Replace lodash with lodash-es for tree shaking */
  'lodash': 'lodash-es',

  /** Use date-fns over moment.js (120KB → 10KB for typical usage) */
  'moment': 'date-fns',
} as const;

/** Verify import is using optimized package */
export function isOptimizedImport(packageName: string): boolean {
  const unoptimized = Object.keys(MODULE_REPLACEMENTS);
  return !unoptimized.includes(packageName);
}
