/**
 * Service Worker Configuration
 *
 * Configuration for the service worker (public/sw.js).
 * Manages registration, updates, and offline strategy.
 */

export const SW_CONFIG = {
  /** Enable service worker */
  enabled: process.env.NEXT_PUBLIC_ENABLE_SW === 'true',

  /** Cache strategies per resource type */
  strategies: {
    staticAssets: 'CacheFirst',
    fonts: 'CacheFirst',
    images: 'StaleWhileRevalidate',
    api: 'NetworkFirst',
    navigation: 'NetworkFirst',
  },

  /** PWA manifest settings */
  manifest: {
    name: 'LankaCommerce Cloud',
    shortName: 'LCC Store',
    description: 'Sri Lankan e-commerce platform',
    startUrl: '/',
    display: 'standalone' as const,
    backgroundColor: '#ffffff',
    themeColor: '#1a365d',
  },
} as const;

/** Register service worker with update handling */
export function registerServiceWorker(): void {
  if (typeof window === 'undefined' || !('serviceWorker' in navigator)) return;
  if (!SW_CONFIG.enabled) return;

  window.addEventListener('load', async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/',
      });

      // Handle updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        if (!newWorker) return;

        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'activated' && navigator.serviceWorker.controller) {
            // New version available — could show update prompt
            if (process.env.NODE_ENV === 'development') {
              console.log('[SW] New version available');
            }
          }
        });
      });
    } catch (error) {
      console.error('[SW] Registration failed:', error);
    }
  });
}
