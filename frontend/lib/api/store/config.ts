// ─── Types ──────────────────────────────────────────────────────────────────

export interface EnvironmentConfig {
  baseURL: string;
  timeout: number;
  retryAttempts: number;
  enableLogging: boolean;
  environment: 'development' | 'staging' | 'production' | 'test';
  version: string;
}

export interface UrlValidationResult {
  isValid: boolean;
  errors: string[];
}

// ─── Environment Detection ──────────────────────────────────────────────────

const ENVIRONMENT_URLS: Record<string, string> = {
  development: 'http://localhost:8000/api/v1/store',
  staging: 'https://staging-api.example.lk/api/v1/store',
  production: 'https://api.example.lk/api/v1/store',
  test: 'http://localhost:8000/api/v1/store',
};

export function detectEnvironment(): EnvironmentConfig['environment'] {
  const env = process.env.NODE_ENV;
  if (env === 'test') return 'test';
  if (env === 'production') return 'production';
  if (process.env.NEXT_PUBLIC_STAGING === 'true') return 'staging';
  return 'development';
}

export function loadEnvironmentConfig(): EnvironmentConfig {
  const environment = detectEnvironment();
  const envUrl = process.env.NEXT_PUBLIC_API_URL;
  const baseURL: string = envUrl
    ? `${envUrl}${getApiPrefix()}`
    : (ENVIRONMENT_URLS[environment] ??
      ENVIRONMENT_URLS.development ??
      'http://localhost:8000/api/v1/store');

  return {
    baseURL,
    timeout: Number(process.env.NEXT_PUBLIC_API_TIMEOUT) || 30000,
    retryAttempts: environment === 'production' ? 3 : 1,
    enableLogging: environment === 'development',
    environment,
    version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
  };
}

// ─── URL Utilities ──────────────────────────────────────────────────────────

export function normalizeUrl(url: string): string {
  return url.replace(/\/+$/, '');
}

export function buildApiUrl(
  path: string,
  params?: Record<string, string | number | boolean | undefined>
): string {
  const config = loadEnvironmentConfig();
  let url = `${normalizeUrl(config.baseURL)}${path.startsWith('/') ? path : `/${path}`}`;

  if (params) {
    const searchParams = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value));
      }
    }
    const queryString = searchParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  return url;
}

export function validateUrl(url: string): UrlValidationResult {
  const errors: string[] = [];

  if (!url) {
    errors.push('URL is required');
    return { isValid: false, errors };
  }

  try {
    new URL(url);
  } catch {
    errors.push('Invalid URL format');
  }

  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    errors.push('URL must start with http:// or https://');
  }

  return { isValid: errors.length === 0, errors };
}

export function getApiPrefix(): string {
  return process.env.NEXT_PUBLIC_API_PREFIX || '/api/v1/store';
}
