/**
 * Newsletter & Email Marketing Types
 */

export type SubscriptionStatus = 'active' | 'unsubscribed' | 'pending' | 'bounced';

export interface NewsletterSubscription {
  id: string;
  email: string;
  name?: string;
  status: SubscriptionStatus;
  preferences: NewsletterPreferences;
  subscribedAt: string;
  source: string;
}

export interface NewsletterPreferences {
  promotions: boolean;
  newArrivals: boolean;
  flashSales: boolean;
  weeklyDigest: boolean;
}

export interface SubscribeRequest {
  email: string;
  name?: string;
  preferences?: Partial<NewsletterPreferences>;
  source?: string;
}

export interface SubscribeResponse {
  success: boolean;
  message: string;
  requiresConfirmation: boolean;
}

export interface UnsubscribeResponse {
  success: boolean;
  message: string;
}

export interface NewsletterFormData {
  email: string;
  name?: string;
  source?: SubscriptionSource;
  preferences?: Partial<NewsletterPreferences>;
}

export type SubscriptionSource = 'footer' | 'popup' | 'checkout' | 'product-page' | 'account' | 'exit-intent';
