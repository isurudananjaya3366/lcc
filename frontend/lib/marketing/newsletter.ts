/**
 * Newsletter API Client
 */

import type { SubscribeRequest, SubscribeResponse, UnsubscribeResponse } from '@/types/marketing/newsletter.types';

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

/** Subscribe to newsletter */
export async function subscribe(data: SubscribeRequest): Promise<SubscribeResponse> {
  return fetchJSON<SubscribeResponse>('/api/webstore/newsletter/subscribe', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/** Unsubscribe from newsletter */
export async function unsubscribe(email: string, token: string): Promise<UnsubscribeResponse> {
  return fetchJSON<UnsubscribeResponse>('/api/webstore/newsletter/unsubscribe', {
    method: 'POST',
    body: JSON.stringify({ email, token }),
  });
}

/** Confirm subscription (double opt-in) */
export async function confirmSubscription(token: string): Promise<SubscribeResponse> {
  return fetchJSON<SubscribeResponse>(`/api/webstore/newsletter/confirm/${encodeURIComponent(token)}`, {
    method: 'POST',
  });
}
