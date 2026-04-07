// ================================================================
// Service Worker Registration — Task 31
// ================================================================
// Utility functions for registering and managing the POS service
// worker from the main thread.
// ================================================================

/** Check whether the current browser supports service workers. */
export function checkServiceWorkerSupport(): boolean {
  return typeof navigator !== 'undefined' && 'serviceWorker' in navigator;
}

/** Register the service worker and return the registration. */
export async function registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
  if (!checkServiceWorkerSupport()) {
    console.warn('[SW] Service workers not supported in this browser');
    return null;
  }

  try {
    const registration = await navigator.serviceWorker.register('/sw.js', {
      scope: '/',
    });

    logServiceWorkerStatus('registered');

    registration.addEventListener('updatefound', () => {
      const newWorker = registration.installing;
      if (newWorker) {
        newWorker.addEventListener('statechange', () => {
          logServiceWorkerStatus(newWorker.state);
        });
      }
    });

    return registration;
  } catch (error) {
    console.error('[SW] Registration failed:', error);
    return null;
  }
}

/** Prompt the waiting worker to activate immediately. */
export async function skipWaiting(): Promise<void> {
  const registration = await navigator.serviceWorker.getRegistration();
  registration?.waiting?.postMessage({ type: 'SKIP_WAITING' });
}

/** Check for an updated service worker. */
export async function checkForUpdates(): Promise<void> {
  const registration = await navigator.serviceWorker.getRegistration();
  await registration?.update();
}

/** Unregister the service worker. */
export async function unregisterServiceWorker(): Promise<void> {
  const registration = await navigator.serviceWorker.getRegistration();
  if (registration) {
    await registration.unregister();
    logServiceWorkerStatus('unregistered');
  }
}

/** Simple status logger. */
export function logServiceWorkerStatus(status: string): void {
  if (typeof console !== 'undefined') {
    console.info(`[SW] Status: ${status}`);
  }
}
