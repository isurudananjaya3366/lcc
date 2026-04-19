/**
 * WhatsApp Integration Types
 */

export type WhatsAppMessageType = 'product_inquiry' | 'order_support' | 'general' | 'cart_share' | 'product_share';

export interface WhatsAppConfig {
  phoneNumber: string;
  defaultCountryCode: string;
  businessName: string;
  workingHours: {
    start: string;
    end: string;
    timezone: string;
    days: number[];
  };
  greeting: string;
  awayMessage: string;
}

export interface WhatsAppMessage {
  type: WhatsAppMessageType;
  text: string;
  phoneNumber?: string;
}

export interface WhatsAppProductInquiry {
  productName: string;
  productUrl: string;
  price: number;
  sku?: string;
}

export interface WhatsAppCartShare {
  items: Array<{ name: string; quantity: number; price: number }>;
  total: number;
  couponCode?: string;
}
