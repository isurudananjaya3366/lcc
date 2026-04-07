// ================================================================
// Base API Client
// ================================================================
// Type-safe fetch wrapper with auth headers, error handling,
// and multi-tenant context support.
//
// Usage:
//   const products = await api.get<Product[]>('/products')
//   await api.post<Product>('/products', newProduct)
// ================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

// ── Types ──────────────────────────────────────────────────────

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, string[]>;
}

// ── API Client ─────────────────────────────────────────────────

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  /**
   * Core request method — all HTTP methods delegate here.
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders(),
        ...this.getTenantHeaders(),
        ...options.headers,
      },
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      throw await this.handleError(response);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  }

  /**
   * Attach JWT bearer token if available.
   */
  private getAuthHeaders(): HeadersInit {
    const token =
      typeof window !== 'undefined'
        ? localStorage.getItem('accessToken')
        : null;

    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  /**
   * Attach tenant context from subdomain.
   */
  private getTenantHeaders(): HeadersInit {
    const hostname =
      typeof window !== 'undefined' ? window.location.hostname : '';
    const tenant = hostname.split('.')[0];

    return tenant ? { 'X-Tenant': tenant } : {};
  }

  /**
   * Parse error response or return a generic error.
   */
  private async handleError(response: Response): Promise<ApiError> {
    try {
      const error = await response.json();
      return error as ApiError;
    } catch {
      return {
        message: `Request failed with status ${response.status}`,
        code: String(response.status),
      };
    }
  }

  // ── HTTP Methods ─────────────────────────────────────────────

  get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  put<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  patch<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

// ── Singleton Instance ─────────────────────────────────────────

export const api = new ApiClient(API_BASE_URL);
