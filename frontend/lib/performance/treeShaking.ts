/**
 * Tree Shaking Configuration & Guidelines
 *
 * Next.js enables tree shaking by default for ES modules.
 * This file documents patterns to ensure maximum dead-code elimination.
 */

export const TREE_SHAKING_CONFIG = {
  /** Packages that should use named imports (not barrel imports) */
  namedImportOnly: [
    'lucide-react',     // Icons: import { Icon } from 'lucide-react'
    'lodash-es',        // Utilities: import { debounce } from 'lodash-es'
    'date-fns',         // Dates: import { format } from 'date-fns'
    '@radix-ui/react-*', // UI primitives
  ],

  /** Packages known to be side-effect free */
  sideEffectFree: [
    'lucide-react',
    'lodash-es',
    'date-fns',
    'clsx',
    'class-variance-authority',
  ],

  /** Import patterns to avoid */
  antiPatterns: [
    'import * as Icons from "lucide-react"',
    'import _ from "lodash"',
    'import moment from "moment"',
    'import { default as * } from "..."',
  ],
} as const;
