import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { setupAuthInterceptor } from './interceptors/auth';
import { setupErrorInterceptor } from './interceptors/errors';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface ApiResponse<T> {
  success: boolean;
  status: number;
  message?: string;
  data: T;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  statusCode: number;
  message: string;
  errors?: ValidationError[];
  stack_trace?: string;
}

export interface ValidationError {
  field: string;
  messages: string[];
}

export interface ClientConfig {
  baseURL: string;
  timeout: number;
  headers: Record<string, string>;
  withCredentials: boolean;
}

// ─── Default Configuration ──────────────────────────────────────────────────

const DEFAULT_STORE_CONFIG: ClientConfig = {
  baseURL: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/store`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    'X-Client-Platform': 'web-store',
    'X-Client-Version': '1.0.0',
    Locale: 'en-LK',
    Timezone: 'Asia/Colombo',
  },
  withCredentials: true,
};

// ─── Singleton Client ───────────────────────────────────────────────────────

let storeClient: AxiosInstance | null = null;
let currentConfig: ClientConfig = { ...DEFAULT_STORE_CONFIG };

function createStoreAxiosInstance(config?: Partial<ClientConfig>): AxiosInstance {
  const mergedConfig = { ...DEFAULT_STORE_CONFIG, ...config };
  currentConfig = mergedConfig;

  const instance = axios.create({
    baseURL: mergedConfig.baseURL,
    timeout: mergedConfig.timeout,
    headers: mergedConfig.headers,
    withCredentials: mergedConfig.withCredentials,
  });

  // Attach interceptors
  setupAuthInterceptor(instance);
  setupErrorInterceptor(instance);

  return instance;
}

export function getStoreClient(config?: Partial<ClientConfig>): AxiosInstance {
  if (!storeClient) {
    storeClient = createStoreAxiosInstance(config);
  }
  return storeClient;
}

export function isConfigured(): boolean {
  return storeClient !== null;
}

export function updateBaseURL(url: string): void {
  currentConfig.baseURL = url;
  if (storeClient) {
    storeClient.defaults.baseURL = url;
  }
}

export function resetStoreClient(): void {
  storeClient = null;
  currentConfig = { ...DEFAULT_STORE_CONFIG };
}

export async function checkClientHealth(): Promise<boolean> {
  try {
    const client = getStoreClient();
    const response = await client.get('/health/', { timeout: 5000 });
    return response.status === 200;
  } catch {
    return false;
  }
}

export { storeClient, currentConfig };
