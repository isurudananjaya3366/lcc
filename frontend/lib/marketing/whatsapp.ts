/**
 * WhatsApp Message Utilities
 */

import { whatsappConfig, buildWhatsAppUrl, isWithinWorkingHours } from '@/config/whatsapp.config';
import type { WhatsAppProductInquiry, WhatsAppCartShare, WhatsAppMessageType } from '@/types/marketing/whatsapp.types';

/** Build product inquiry message */
export function buildProductInquiryMessage(product: WhatsAppProductInquiry): string {
  const lines = [
    `Hi! I'm interested in this product:`,
    ``,
    `*${product.productName}*`,
    `Price: ₨${product.price.toLocaleString()}`,
  ];
  if (product.sku) lines.push(`SKU: ${product.sku}`);
  lines.push(``, `Link: ${product.productUrl}`, ``, `Could you provide more details?`);
  return lines.join('\n');
}

/** Build cart share message */
export function buildCartShareMessage(cart: WhatsAppCartShare): string {
  const lines = [`Hi! I'd like to order the following items:`, ``];
  cart.items.forEach((item, i) => {
    lines.push(`${i + 1}. ${item.name} x${item.quantity} — ₨${(item.price * item.quantity).toLocaleString()}`);
  });
  lines.push(``, `*Total: ₨${cart.total.toLocaleString()}*`);
  if (cart.couponCode) lines.push(`Coupon: ${cart.couponCode}`);
  lines.push(``, `Please confirm availability and delivery.`);
  return lines.join('\n');
}

/** Build order support message */
export function buildOrderSupportMessage(orderId: string): string {
  return `Hi! I need help with my order #${orderId}. Could you please check the status?`;
}

/** Build general inquiry message */
export function buildGeneralMessage(subject?: string): string {
  return subject ? `Hi! I have a question about: ${subject}` : whatsappConfig.greeting;
}

/** Get WhatsApp URL for a specific message type */
export function getWhatsAppUrl(type: WhatsAppMessageType, data?: Record<string, unknown>): string {
  let message: string;

  switch (type) {
    case 'product_inquiry':
      message = buildProductInquiryMessage(data as unknown as WhatsAppProductInquiry);
      break;
    case 'cart_share':
      message = buildCartShareMessage(data as unknown as WhatsAppCartShare);
      break;
    case 'order_support':
      message = buildOrderSupportMessage((data?.orderId as string) || '');
      break;
    default:
      message = buildGeneralMessage(data?.subject as string);
  }

  return buildWhatsAppUrl(whatsappConfig.phoneNumber, message);
}

/** Get online status info */
export function getWhatsAppStatus(): { isOnline: boolean; message: string } {
  const online = isWithinWorkingHours(whatsappConfig);
  return {
    isOnline: online,
    message: online ? whatsappConfig.greeting : whatsappConfig.awayMessage,
  };
}
