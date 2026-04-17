/**
 * GridConfig — Task 18
 *
 * Grid layout configuration constants and helpers for the product catalog.
 * Centralizes column counts, gap sizes, and breakpoint definitions so that
 * ProductGrid and any consuming component stay in sync.
 */

// ── Breakpoints ────────────────────────────────────────────────

export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const;

// ── Column Counts ──────────────────────────────────────────────

export interface GridColumns {
  mobile: number; // < 640px
  sm: number; // ≥ 640px
  md: number; // ≥ 768px
  lg: number; // ≥ 1024px
  xl: number; // ≥ 1280px
}

export const DEFAULT_GRID_COLUMNS: GridColumns = {
  mobile: 2,
  sm: 2,
  md: 3,
  lg: 4,
  xl: 4,
};

// ── Gap Sizes ─────────────────────────────────────────────────

export interface GridGaps {
  mobile: string; // < 640px
  sm: string; // ≥ 640px
  lg: string; // ≥ 1024px
}

export const DEFAULT_GRID_GAPS: GridGaps = {
  mobile: '0.75rem', // 12px — gap-3
  sm: '1rem', // 16px — sm:gap-4
  lg: '1.25rem', // 20px — lg:gap-5
};

// ── Tailwind Class Helpers ────────────────────────────────────

/**
 * Returns the default product grid Tailwind classes.
 * Matches DEFAULT_GRID_COLUMNS / DEFAULT_GRID_GAPS.
 */
export function getGridClasses(columns?: Partial<GridColumns>): string {
  const cols = { ...DEFAULT_GRID_COLUMNS, ...columns };

  const colMap: Record<number, string> = {
    1: 'grid-cols-1',
    2: 'grid-cols-2',
    3: 'grid-cols-3',
    4: 'grid-cols-4',
    5: 'grid-cols-5',
    6: 'grid-cols-6',
  };
  const smColMap: Record<number, string> = {
    1: 'sm:grid-cols-1',
    2: 'sm:grid-cols-2',
    3: 'sm:grid-cols-3',
    4: 'sm:grid-cols-4',
    5: 'sm:grid-cols-5',
  };
  const lgColMap: Record<number, string> = {
    1: 'lg:grid-cols-1',
    2: 'lg:grid-cols-2',
    3: 'lg:grid-cols-3',
    4: 'lg:grid-cols-4',
    5: 'lg:grid-cols-5',
  };
  const xlColMap: Record<number, string> = {
    1: 'xl:grid-cols-1',
    2: 'xl:grid-cols-2',
    3: 'xl:grid-cols-3',
    4: 'xl:grid-cols-4',
    5: 'xl:grid-cols-5',
  };

  return [
    colMap[cols.mobile] ?? 'grid-cols-2',
    smColMap[cols.sm] ?? 'sm:grid-cols-2',
    lgColMap[cols.lg] ?? 'lg:grid-cols-4',
    xlColMap[cols.xl] ?? 'xl:grid-cols-4',
    'gap-3 sm:gap-4 lg:gap-5',
  ].join(' ');
}

/** Number of skeleton cards shown in loading state */
export const SKELETON_COUNT = 8;
