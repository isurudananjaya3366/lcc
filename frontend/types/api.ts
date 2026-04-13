/**
 * API Type Definitions
 *
 * Contains TypeScript types for API communication including:
 * - Generic response wrappers
 * - Pagination structures
 * - Error formats
 * - Request configurations
 *
 * These types align with Django REST Framework response formats
 * and ensure type safety across all API interactions.
 */

import type { AxiosRequestConfig } from 'axios';

// ── Response Types ─────────────────────────────────────────────

/**
 * Generic API response wrapper.
 * All successful API responses conform to this structure.
 */
export interface APIResponse<T> {
  data: T;
  message?: string;
  timestamp: string;
}

/**
 * Paginated API response for list endpoints.
 * Maps from Django REST Framework's PageNumberPagination format.
 */
export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    pageSize: number;
    totalPages: number;
    totalCount: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
  message?: string;
  timestamp: string;
}

// ── Error Types ────────────────────────────────────────────────

/**
 * Structured API error format.
 * Maps from Django REST Framework error responses.
 */
export interface APIError {
  code: string;
  message: string;
  details?: Record<string, string[]>;
  timestamp: string;
}

/**
 * Known API error codes returned by the backend.
 */
export type APIErrorCode =
  | 'validation_error'
  | 'not_found'
  | 'unauthorized'
  | 'forbidden'
  | 'server_error'
  | 'conflict'
  | 'rate_limit';

// ── Request Types ──────────────────────────────────────────────

/**
 * Custom request configuration extending Axios defaults.
 * Use for per-request overrides (timeout, headers, params, etc.).
 */
export type RequestConfig = AxiosRequestConfig;

// ── Query Parameter Types ──────────────────────────────────────

/**
 * Common query parameters for paginated list endpoints.
 */
export interface PaginationParams {
  page?: number;
  page_size?: number;
}

/**
 * Common query parameters for searchable endpoints.
 */
export interface SearchParams extends PaginationParams {
  search?: string;
  ordering?: string;
}

/**
 * Common filter parameters.
 */
export interface FilterParams extends SearchParams {
  [key: string]: string | number | boolean | undefined;
}

// ── Sorting Types ──────────────────────────────────────────────

export type SortDirection = 'asc' | 'desc';

export interface SortConfig {
  field: string;
  direction: SortDirection;
}
