/**
 * Storefront Common / Shared Types
 */

export interface StoreCurrency {
  code: string;
  symbol: string;
  locale: string;
  decimalPlaces: number;
}

export type StoreLocale = 'en-LK' | 'si-LK';

export interface StorePagination {
  page: number;
  pageSize: number;
  totalPages: number;
  totalItems: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

export interface StoreSortOption {
  field: string;
  direction: 'asc' | 'desc';
}

export interface StoreFilterOption {
  field: string;
  operator: 'eq' | 'gt' | 'lt' | 'in' | 'contains';
  value: unknown;
}

export enum StoreLoadingState {
  IDLE = 'idle',
  LOADING = 'loading',
  SUCCESS = 'success',
  ERROR = 'error',
}

export interface StoreApiStatus {
  status: StoreLoadingState;
  isLoading: boolean;
  isError: boolean;
  error?: string;
  lastFetch?: string;
}

export interface StoreErrorResponse {
  message: string;
  code: string;
  status: number;
  details?: Record<string, unknown>;
}

export interface StoreSuccessResponse<T> {
  data: T;
  status: 'success';
  message?: string;
  timestamp: string;
}
