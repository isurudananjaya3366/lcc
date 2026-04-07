// ================================================================
// className Utility (cn)
// ================================================================
// Combines clsx (conditional classes) with tailwind-merge
// (conflict resolution) for a single, reliable className helper.
//
// Usage:
//   cn('p-2', 'p-4')                          → 'p-4'
//   cn('btn', isActive && 'btn-active')        → conditional
//   cn('text-sm', className)                   → merge with prop
// ================================================================

import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
