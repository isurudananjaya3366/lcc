// ================================================================
// Theme API Service
// ================================================================
// Handles all API communication for theme data.
// ================================================================

import type { Theme, PartialTheme, ThemeApiResponse } from '@/types/storefront/theme.types';

// ─── Config ─────────────────────────────────────────────────────

const API_BASE = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/store`;
const THEME_ENDPOINT = `${API_BASE}/theme`;
const REQUEST_TIMEOUT = 10000;

// ─── Helpers ────────────────────────────────────────────────────

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

  try {
    const res = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!res.ok) {
      const errorBody = await res.json().catch(() => ({}));
      throw new ThemeServiceError(
        errorBody.message || `Request failed with status ${res.status}`,
        res.status
      );
    }

    return res.json();
  } finally {
    clearTimeout(timeoutId);
  }
}

// ─── Error Class ────────────────────────────────────────────────

export class ThemeServiceError extends Error {
  constructor(
    message: string,
    public statusCode?: number
  ) {
    super(message);
    this.name = 'ThemeServiceError';
  }
}

// ─── Service Functions ──────────────────────────────────────────

export async function fetchTheme(tenantId?: string): Promise<Theme> {
  const url = tenantId
    ? `${THEME_ENDPOINT}?tenantId=${encodeURIComponent(tenantId)}`
    : THEME_ENDPOINT;
  const response = await request<ThemeApiResponse>(url);
  return response.data.theme;
}

export async function fetchThemeById(id: string): Promise<Theme> {
  const response = await request<ThemeApiResponse>(`${THEME_ENDPOINT}/${encodeURIComponent(id)}`);
  return response.data.theme;
}

export async function updateThemeApi(id: string, updates: PartialTheme): Promise<Theme> {
  const response = await request<ThemeApiResponse>(`${THEME_ENDPOINT}/${encodeURIComponent(id)}`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
  return response.data.theme;
}

export async function createTheme(
  theme: Omit<Theme, 'id' | 'createdAt' | 'updatedAt'>
): Promise<Theme> {
  const response = await request<ThemeApiResponse>(THEME_ENDPOINT, {
    method: 'POST',
    body: JSON.stringify(theme),
  });
  return response.data.theme;
}

export async function deleteTheme(id: string): Promise<void> {
  await request<{ success: boolean }>(`${THEME_ENDPOINT}/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  });
}

export async function getDefaultTheme(): Promise<Theme> {
  const response = await request<ThemeApiResponse>(`${THEME_ENDPOINT}/default`);
  return response.data.theme;
}
