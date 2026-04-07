// ================================================================
// General Utility Functions
// ================================================================
// Pure, framework-agnostic helpers. No React dependencies.
// All functions are individually exported for tree-shaking.
// ================================================================

// ── Type Guards ────────────────────────────────────────────────

/**
 * Check if a value is defined (not null or undefined).
 */
export const isDefined = <T>(value: T | undefined | null): value is T => {
  return value !== undefined && value !== null;
};

/**
 * Check if a value is a string.
 */
export const isString = (value: unknown): value is string => {
  return typeof value === 'string';
};

/**
 * Check if a value is a number (and not NaN).
 */
export const isNumber = (value: unknown): value is number => {
  return typeof value === 'number' && !isNaN(value);
};

// ── Array Helpers ──────────────────────────────────────────────

/**
 * Check if an array is empty, null, or undefined.
 */
export const isEmpty = <T>(arr: T[] | undefined | null): boolean => {
  return !arr || arr.length === 0;
};

/**
 * Generate an array of numbers from start (inclusive) to end (exclusive).
 */
export const range = (start: number, end: number): number[] => {
  return Array.from({ length: end - start }, (_, i) => start + i);
};

/**
 * Group an array of items by a key function.
 */
export const groupBy = <T, K extends keyof never>(
  array: T[],
  keyFn: (item: T) => K
): Record<K, T[]> => {
  return array.reduce(
    (acc, item) => {
      const key = keyFn(item);
      acc[key] = [...(acc[key] || []), item];
      return acc;
    },
    {} as Record<K, T[]>
  );
};

// ── Async Helpers ──────────────────────────────────────────────

/**
 * Pause execution for the specified number of milliseconds.
 */
export const sleep = (ms: number): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

/**
 * Create a debounced version of a function.
 */
export const debounce = <T extends (...args: never[]) => void>(
  fn: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};

/**
 * Create a throttled version of a function.
 */
export const throttle = <T extends (...args: never[]) => void>(
  fn: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle = false;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
};

// ── Number Helpers ─────────────────────────────────────────────

/**
 * Clamp a number between min and max values.
 */
export const clamp = (value: number, min: number, max: number): number => {
  return Math.min(Math.max(value, min), max);
};

// ── Object Helpers ─────────────────────────────────────────────

/**
 * Create a new object with specified keys omitted.
 */
export const omit = <T extends object, K extends keyof T>(
  obj: T,
  keys: K[]
): Omit<T, K> => {
  const result = { ...obj };
  keys.forEach((key) => delete result[key]);
  return result;
};

/**
 * Create a new object with only the specified keys.
 */
export const pick = <T extends object, K extends keyof T>(
  obj: T,
  keys: K[]
): Pick<T, K> => {
  const result = {} as Pick<T, K>;
  keys.forEach((key) => {
    if (key in obj) result[key] = obj[key];
  });
  return result;
};
