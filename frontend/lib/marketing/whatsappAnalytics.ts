/**
 * WhatsApp Analytics — tracks WhatsApp interaction events.
 */

export type WhatsAppClickType = 'product_inquiry' | 'cart_share' | 'order_support' | 'general';

interface WhatsAppClickPayload {
  type: WhatsAppClickType;
  context?: Record<string, unknown>;
  timestamp: string;
}

/**
 * Track a WhatsApp button click event.
 * Emits to the analytics layer (window.dataLayer / GA4 / internal analytics).
 */
export function trackWhatsAppClick(
  type: WhatsAppClickType,
  context?: Record<string, unknown>
): void {
  const payload: WhatsAppClickPayload = {
    type,
    context,
    timestamp: new Date().toISOString(),
  };

  // Google Analytics / GTM dataLayer
  if (typeof window !== 'undefined') {
    const w = window as Window & { dataLayer?: unknown[] };
    if (Array.isArray(w.dataLayer)) {
      w.dataLayer.push({
        event: 'whatsapp_click',
        whatsapp_click_type: type,
        ...context,
      });
    }
  }

  // Internal analytics endpoint (best-effort, non-blocking)
  const apiBase = process.env.NEXT_PUBLIC_API_URL || '';
  fetch(`${apiBase}/api/webstore/analytics/whatsapp-click`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    keepalive: true,
  }).catch(() => {
    // Silently ignore — analytics must not break user flows
  });
}
