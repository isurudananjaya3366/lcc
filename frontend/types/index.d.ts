/**
 * Global type declarations for LankaCommerce Cloud.
 *
 * Provides utility types, API response types, and common
 * type aliases used across the entire frontend application.
 */

// ── Utility Types ──────────────────────────────────────────────

/** Make a type nullable (T | null). */
type Nullable<T> = T | null;

/** Make a type optional (T | undefined). */
type Optional<T> = T | undefined;

/** Extract the return type of an async function. */
type AsyncReturnType<T extends (...args: unknown[]) => Promise<unknown>> = T extends (
  ...args: unknown[]
) => Promise<infer R>
  ? R
  : never;

// ── Common Aliases ─────────────────────────────────────────────

/** UUID string identifier. */
type ID = string;

/** ISO 8601 date-time string. */
type Timestamp = string;

/** Sri Lankan Rupee amount (numeric). */
type Currency = number;

// ── API Response Types ─────────────────────────────────────────

/** Standard API response wrapper. */
interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

/** Paginated list API response. */
interface PaginatedResponse<T> {
  data: T[];
  count: number;
  next: Nullable<string>;
  previous: Nullable<string>;
  page: number;
  pageSize: number;
  totalPages: number;
}

/** Standard API error response. */
interface ApiError {
  message: string;
  code: string;
  status: number;
  details?: Record<string, string[]>;
}
