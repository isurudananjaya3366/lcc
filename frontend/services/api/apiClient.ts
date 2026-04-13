/**
 * API Client — Axios-based HTTP client for LankaCommerce Cloud.
 *
 * Provides a pre-configured Axios instance with:
 * - Base URL from NEXT_PUBLIC_API_URL environment variable
 * - Default JSON headers (Content-Type, Accept)
 * - 30-second request timeout
 * - CORS credentials (withCredentials) for cookie-based auth
 *
 * Also exports a factory function for creating custom instances.
 *
 * @example
 * import apiClient from '@/services/api/apiClient';
 * const response = await apiClient.get<Product[]>('/products');
 *
 * @example
 * import { createApiClient } from '@/services/api/apiClient';
 * const uploadClient = createApiClient({ timeout: 120000 });
 */

import axios from 'axios';
import type { AxiosInstance, AxiosRequestConfig } from 'axios';
import { requestInterceptor, requestErrorHandler } from './interceptors/request.interceptor';
import {
  responseSuccessHandler,
  createResponseErrorHandler,
} from './interceptors/response.interceptor';

// ── Default Configuration ──────────────────────────────────────

export const DEFAULT_CONFIG: AxiosRequestConfig = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
};

// ── Base API Client ────────────────────────────────────────────

const apiClient: AxiosInstance = axios.create(DEFAULT_CONFIG);

// Register interceptors
apiClient.interceptors.request.use(requestInterceptor, requestErrorHandler);
apiClient.interceptors.response.use(responseSuccessHandler, createResponseErrorHandler(apiClient));

// ── Factory Function ───────────────────────────────────────────

/**
 * Creates a custom API client instance with optional configuration overrides.
 *
 * Use this when you need an isolated Axios instance with different settings
 * (e.g., extended timeout for uploads, different base URL for microservices).
 *
 * @param config - Optional Axios configuration overrides
 * @returns Configured Axios instance
 *
 * @example
 * const uploadClient = createApiClient({ timeout: 120000 });
 *
 * @example
 * const authClient = createApiClient({
 *   baseURL: 'https://auth.example.com/api',
 * });
 */
export function createApiClient(config?: Partial<AxiosRequestConfig>): AxiosInstance {
  return axios.create({
    ...DEFAULT_CONFIG,
    ...config,
    headers: {
      ...DEFAULT_CONFIG.headers,
      ...config?.headers,
    },
  });
}

export { apiClient };
export default apiClient;
