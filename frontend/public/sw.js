// ================================================================
// Service Worker — Task 32
// ================================================================
// Workbox-based service worker for caching static assets,
// product images, and API responses.
//
// This file is the SW *source* — it runs inside the worker context.
// ================================================================

/* eslint-disable no-restricted-globals */

const CACHE_NAMES = {
  STATIC_ASSETS:   'static-assets-v1',
  FONTS:           'fonts-v1',
  APP_IMAGES:      'app-images-v1',
  PRODUCT_IMAGES:  'product-images-v1',
  API_RESPONSES:   'api-responses-v1',
};

const OFFLINE_PAGE = '/offline.html';
const SYNC_CHANNEL = 'pos-sync-channel';

// Maximum entries per cache and max age in seconds
const CACHE_LIMITS = {
  [CACHE_NAMES.STATIC_ASSETS]:  { maxEntries: 100, maxAgeSeconds: 30 * 24 * 3600 },   // 30 days
  [CACHE_NAMES.FONTS]:          { maxEntries: 30,  maxAgeSeconds: 365 * 24 * 3600 },   // 1 year
  [CACHE_NAMES.APP_IMAGES]:     { maxEntries: 100, maxAgeSeconds: 30 * 24 * 3600 },
  [CACHE_NAMES.PRODUCT_IMAGES]: { maxEntries: 500, maxAgeSeconds: 7 * 24 * 3600 },     // 7 days
  [CACHE_NAMES.API_RESPONSES]:  { maxEntries: 200, maxAgeSeconds: 24 * 3600 },          // 1 day
};

// ── Install ────────────────────────────────────────────────────

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAMES.STATIC_ASSETS).then((cache) =>
      cache.addAll([OFFLINE_PAGE]),
    ),
  );
});

// ── Activate — clean up old caches ─────────────────────────────

self.addEventListener('activate', (event) => {
  const validNames = new Set(Object.values(CACHE_NAMES));
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => !validNames.has(key))
          .map((key) => caches.delete(key)),
      ),
    ),
  );
});

// ── Skip-waiting message ───────────────────────────────────────

self.addEventListener('message', (event) => {
  if (event.data?.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// ── Fetch strategy router ──────────────────────────────────────

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Static assets — Cache First
  if (isStaticAsset(url)) {
    event.respondWith(cacheFirst(request, CACHE_NAMES.STATIC_ASSETS));
    return;
  }

  // Fonts — Cache First (long TTL)
  if (isFont(url)) {
    event.respondWith(cacheFirst(request, CACHE_NAMES.FONTS));
    return;
  }

  // App images — Cache First
  if (isAppImage(url)) {
    event.respondWith(cacheFirst(request, CACHE_NAMES.APP_IMAGES));
    return;
  }

  // Product images — Stale While Revalidate
  if (isProductImage(url)) {
    event.respondWith(staleWhileRevalidate(request, CACHE_NAMES.PRODUCT_IMAGES));
    return;
  }

  // API calls — Network First (3 s timeout)
  if (isApiRequest(url)) {
    event.respondWith(networkFirst(request, CACHE_NAMES.API_RESPONSES, 3000));
    return;
  }

  // Navigation — Network with offline fallback
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() => caches.match(OFFLINE_PAGE)),
    );
    return;
  }
});

// ── Background sync (Task 33) ──────────────────────────────────

self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-transactions') {
    event.waitUntil(syncPendingTransactions());
  }
});

async function syncPendingTransactions() {
  const channel = new BroadcastChannel(SYNC_CHANNEL);
  channel.postMessage({ type: 'sync-started', tag: 'sync-transactions', timestamp: new Date().toISOString() });

  try {
    // The actual sync logic is delegated to the main thread via postMessage
    // because IndexedDB access from SW is limited. Signal the client.
    const clients = await self.clients.matchAll({ type: 'window' });
    for (const client of clients) {
      client.postMessage({ type: 'SYNC_TRANSACTIONS' });
    }
    channel.postMessage({ type: 'sync-complete', tag: 'sync-transactions', timestamp: new Date().toISOString() });
  } catch (error) {
    channel.postMessage({
      type: 'sync-failed',
      tag: 'sync-transactions',
      payload: { error: String(error) },
      timestamp: new Date().toISOString(),
    });
  } finally {
    channel.close();
  }
}

// ── URL matchers ───────────────────────────────────────────────

function isStaticAsset(url) {
  return /\.(js|css)$/.test(url.pathname) && !url.pathname.startsWith('/api');
}

function isFont(url) {
  return /\.(woff2?|ttf|otf|eot)$/.test(url.pathname);
}

function isAppImage(url) {
  return url.pathname.startsWith('/images/') || url.pathname.startsWith('/icons/');
}

function isProductImage(url) {
  return url.pathname.startsWith('/media/products/');
}

function isApiRequest(url) {
  return url.pathname.startsWith('/api/');
}

// ── Cache strategies ───────────────────────────────────────────

async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response.ok) {
    const cache = await caches.open(cacheName);
    cache.put(request, response.clone());
    enforceCacheLimits(cacheName);
  }
  return response;
}

async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);

  const fetchPromise = fetch(request).then((response) => {
    if (response.ok) {
      cache.put(request, response.clone());
      enforceCacheLimits(cacheName);
    }
    return response;
  }).catch(() => cached);

  return cached || fetchPromise;
}

async function networkFirst(request, cacheName, timeoutMs) {
  const cache = await caches.open(cacheName);

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    const response = await fetch(request, { signal: controller.signal });
    clearTimeout(timeoutId);

    if (response.ok) {
      cache.put(request, response.clone());
      enforceCacheLimits(cacheName);
    }
    return response;
  } catch {
    const cached = await cache.match(request);
    return cached || new Response('Offline', { status: 503 });
  }
}

// ── Cache limit enforcement ────────────────────────────────────

async function enforceCacheLimits(cacheName) {
  const limits = CACHE_LIMITS[cacheName];
  if (!limits) return;

  try {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();

    if (keys.length > limits.maxEntries) {
      // Evict oldest entries (FIFO) until under limit
      const toDelete = keys.slice(0, keys.length - limits.maxEntries);
      for (const key of toDelete) {
        await cache.delete(key);
      }
    }
  } catch {
    // Best-effort — don't let cleanup errors affect requests
  }
}
