/**
 * Flash Sale API Client
 */

import type { FlashSale, FlashSaleListItem } from '@/types/marketing/flash-sale.types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(error.message || `HTTP ${res.status}`);
  }
  return res.json();
}

/** Get all active and upcoming flash sales */
export async function getFlashSales(): Promise<FlashSaleListItem[]> {
  return fetchJSON<FlashSaleListItem[]>('/api/webstore/flash-sales');
}

/** Get flash sale details by slug */
export async function getFlashSaleBySlug(slug: string): Promise<FlashSale> {
  return fetchJSON<FlashSale>(`/api/webstore/flash-sales/${encodeURIComponent(slug)}`);
}

/** Get currently active flash sales for homepage banner */
export async function getActiveFlashSales(): Promise<FlashSaleListItem[]> {
  return fetchJSON<FlashSaleListItem[]>('/api/webstore/flash-sales/active');
}

/** Get featured flash sale products */
export async function getFeaturedFlashSaleProducts(): Promise<FlashSale['products']> {
  return fetchJSON<FlashSale['products']>('/api/webstore/flash-sales/featured-products');
}

/** Get upcoming flash sales (scheduled but not yet started) */
export async function getUpcomingSales(): Promise<FlashSaleListItem[]> {
  return fetchJSON<FlashSaleListItem[]>('/api/webstore/flash-sales/upcoming');
}

/** Get seasonal flash sales (e.g. avurudu, christmas) */
export async function getSeasonalSales(season: string): Promise<FlashSaleListItem[]> {
  return fetchJSON<FlashSaleListItem[]>(`/api/webstore/flash-sales/seasonal/${encodeURIComponent(season)}`);
}
