// ================================================================
// Sync API Mock Handlers — Task 87
// ================================================================
// Provides configurable mock API responses for sync engine tests.
// Can be used with fetch mocking or MSW when available.
// ================================================================

/* eslint-disable @typescript-eslint/no-explicit-any */

export interface MockSyncResponse {
  synced: Array<{ offline_id: string; server_id: string }>;
  conflicts: Array<{ id: string; entity_id: string; type: string }>;
  updated: Array<Record<string, unknown>>;
}

export interface MockPullResponse {
  results: Array<Record<string, unknown>>;
  next: string | null;
  count: number;
  last_sync_timestamp: string;
}

// ── Default responses ──────────────────────────────────────────

export const defaultPushResponse: MockSyncResponse = {
  synced: [],
  conflicts: [],
  updated: [],
};

export const defaultPullResponse: MockPullResponse = {
  results: [],
  next: null,
  count: 0,
  last_sync_timestamp: new Date().toISOString(),
};

// ── Configurable mock state ────────────────────────────────────

let pushResponse: MockSyncResponse = { ...defaultPushResponse };
let pullResponse: MockPullResponse = { ...defaultPullResponse };
let pushStatusCode = 200;
let pullStatusCode = 200;
let shouldRejectPush = false;
let shouldRejectPull = false;
let pushDelay = 0;
let pullDelay = 0;

// ── Configuration API ──────────────────────────────────────────

export function configurePushResponse(
  response: Partial<MockSyncResponse>,
  statusCode = 200
): void {
  pushResponse = { ...defaultPushResponse, ...response };
  pushStatusCode = statusCode;
}

export function configurePullResponse(
  response: Partial<MockPullResponse>,
  statusCode = 200
): void {
  pullResponse = { ...defaultPullResponse, ...response };
  pullStatusCode = statusCode;
}

export function configurePushFailure(reject = true): void {
  shouldRejectPush = reject;
}

export function configurePullFailure(reject = true): void {
  shouldRejectPull = reject;
}

export function configurePushDelay(ms: number): void {
  pushDelay = ms;
}

export function configurePullDelay(ms: number): void {
  pullDelay = ms;
}

export function resetMockSyncApi(): void {
  pushResponse = { ...defaultPushResponse };
  pullResponse = { ...defaultPullResponse };
  pushStatusCode = 200;
  pullStatusCode = 200;
  shouldRejectPush = false;
  shouldRejectPull = false;
  pushDelay = 0;
  pullDelay = 0;
}

// ── Mock fetch handler ─────────────────────────────────────────

function delay(ms: number): Promise<void> {
  return ms > 0 ? new Promise((r) => setTimeout(r, ms)) : Promise.resolve();
}

/**
 * A mock fetch function that can be assigned to `globalThis.fetch`.
 * Routes push/pull/health endpoints to configurable responses.
 */
export async function mockSyncFetch(
  input: RequestInfo | URL,
  init?: RequestInit
): Promise<Response> {
  const url = typeof input === 'string' ? input : input.toString();

  // Health check endpoint
  if (url.includes('/api/health') || url.includes('/health/')) {
    return new Response('OK', { status: 200 });
  }

  // Push endpoint
  if (
    url.includes('/sync/push') ||
    (init?.method === 'POST' && url.includes('/sync'))
  ) {
    await delay(pushDelay);
    if (shouldRejectPush) throw new Error('Network error (mock)');
    return new Response(JSON.stringify(pushResponse), {
      status: pushStatusCode,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // Pull endpoint
  if (
    url.includes('/sync/pull') ||
    (init?.method === 'GET' && url.includes('/sync'))
  ) {
    await delay(pullDelay);
    if (shouldRejectPull) throw new Error('Network error (mock)');
    return new Response(JSON.stringify(pullResponse), {
      status: pullStatusCode,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // Default: 404
  return new Response('Not Found', { status: 404 });
}
