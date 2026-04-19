/**
 * WhatsApp Business Configuration
 */

import type { WhatsAppConfig } from '@/types/marketing/whatsapp.types';

export const whatsappConfig: WhatsAppConfig = {
  phoneNumber: process.env.NEXT_PUBLIC_WHATSAPP_NUMBER || '+94771234567',
  defaultCountryCode: '+94',
  businessName: process.env.NEXT_PUBLIC_BUSINESS_NAME || 'Store',
  workingHours: {
    start: '09:00',
    end: '18:00',
    timezone: 'Asia/Colombo',
    days: [1, 2, 3, 4, 5, 6], // Mon-Sat
  },
  greeting: 'Hi! How can we help you today?',
  awayMessage: "We're currently offline. Leave a message and we'll get back to you!",
};

/** Build WhatsApp click-to-chat URL */
export function buildWhatsAppUrl(phoneNumber: string, message: string): string {
  const cleanPhone = phoneNumber.replace(/[^\d+]/g, '');
  const encoded = encodeURIComponent(message);
  return `https://wa.me/${cleanPhone.replace('+', '')}?text=${encoded}`;
}

/** Check if currently within working hours */
export function isWithinWorkingHours(config: WhatsAppConfig): boolean {
  const now = new Date();
  const formatter = new Intl.DateTimeFormat('en-US', {
    timeZone: config.workingHours.timezone,
    hour: 'numeric',
    minute: 'numeric',
    hour12: false,
    weekday: 'short',
  });

  const parts = formatter.formatToParts(now);
  const hour = parseInt(parts.find((p) => p.type === 'hour')?.value || '0', 10);
  const minute = parseInt(parts.find((p) => p.type === 'minute')?.value || '0', 10);
  const dayStr = parts.find((p) => p.type === 'weekday')?.value || '';
  const dayMap: Record<string, number> = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
  const dayNum = dayMap[dayStr] ?? now.getDay();

  if (!config.workingHours.days.includes(dayNum)) return false;

  const [startH, startM] = config.workingHours.start.split(':').map(Number);
  const [endH, endM] = config.workingHours.end.split(':').map(Number);
  const currentMinutes = hour * 60 + minute;

  return currentMinutes >= startH * 60 + startM && currentMinutes <= endH * 60 + endM;
}
