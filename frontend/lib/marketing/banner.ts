/**
 * Banner API Client
 */

import type { Banner, BannerPosition } from '@/types/marketing/banner.types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(error.message || `HTTP ${res.status}`);
  }
  return res.json();
}

/** Get banners by position */
export async function getBannersByPosition(position: BannerPosition): Promise<Banner[]> {
  return fetchJSON<Banner[]>(`/api/webstore/banners?position=${encodeURIComponent(position)}`);
}

/** Get all active banners */
export async function getActiveBanners(): Promise<Banner[]> {
  return fetchJSON<Banner[]>('/api/webstore/banners/active');
}

/** Get hero carousel banners */
export async function getHeroBanners(): Promise<Banner[]> {
  return fetchJSON<Banner[]>('/api/webstore/banners?position=hero');
}

/** Track banner click */
export async function trackBannerClick(bannerId: string): Promise<void> {
  await fetch(`${API_BASE}/api/webstore/banners/${encodeURIComponent(bannerId)}/click`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
}

/** Get a single banner by id */
export async function getBannerById(id: string): Promise<Banner> {
  return fetchJSON<Banner>(`/api/webstore/banners/${encodeURIComponent(id)}`);
}

/** Record a banner impression (view) */
export async function recordBannerImpression(id: string): Promise<void> {
  await fetch(`${API_BASE}/api/webstore/banners/${encodeURIComponent(id)}/impression`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
}
