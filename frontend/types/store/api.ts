/**
 * Storefront API Response Types
 */

export interface StoreApiResponse<T> {
  data: T;
  status: string;
  message?: string;
  timestamp: string;
}

export interface StorePaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    pageSize: number;
    totalPages: number;
    totalCount: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
}

// ─── Type Guards ─────────────────────────────────────────────────────────────

export function isStoreApiResponse<T>(obj: unknown): obj is StoreApiResponse<T> {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'data' in obj &&
    'status' in obj
  );
}

export function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export function isValidPhone(phone: string): boolean {
  const cleaned = phone.replace(/[\s-]/g, '');
  return /^(\+94|0)(7[0-9])[0-9]{7}$/.test(cleaned);
}

export function isValidPostalCode(code: string): boolean {
  return /^\d{5}$/.test(code);
}
