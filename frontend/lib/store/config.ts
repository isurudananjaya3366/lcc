/**
 * Store Configuration
 *
 * Centralized configuration for the LankaCommerce storefront.
 * Combines store info, API, currency, locale, features, and metadata.
 */

// ─── Store Info ──────────────────────────────────────────────────────────────

export const storeInfo = {
  name: {
    full: 'LankaCommerce Cloud',
    short: 'LankaCommerce',
    display: 'LankaCommerce',
  },
  tagline: 'Your trusted online marketplace in Sri Lanka',
  description: {
    short: 'Shop quality products with seamless checkout and fast delivery island-wide.',
    long: "LankaCommerce Cloud is Sri Lanka's premier e-commerce platform offering electronics, fashion, home & garden, health & beauty products with secure checkout, multiple payment options including COD, and island-wide delivery.",
  },
  branding: {
    primaryColor: '#16a34a',
    secondaryColor: '#f97316',
    logoUrl: '/images/logo.svg',
    faviconUrl: '/favicon.ico',
  },
  contact: {
    email: 'info@lankacommerce.lk',
    supportEmail: 'support@lankacommerce.lk',
    phone: '+94 11 234 5678',
    whatsapp: '+94 77 123 4567',
  },
  businessRegistration: 'PV 12345',
} as const;

// ─── API Config ──────────────────────────────────────────────────────────────

export const apiConfig = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  storeUrl: process.env.NEXT_PUBLIC_STORE_URL || 'http://localhost:3000',
  timeout: 30000,
  retries: 1,
} as const;

// ─── Currency Config ─────────────────────────────────────────────────────────

export const currencyConfig = {
  code: 'LKR',
  symbol: '₨',
  decimalPlaces: 2,
  thousandSeparator: ',',
  decimalSeparator: '.',
  symbolPosition: 'before' as const,
} as const;

/**
 * Format a number as LKR currency.
 * @example formatCurrency(1234.5) → "₨ 1,234.50"
 */
export function formatCurrency(amount: number, options?: { hideSymbol?: boolean }): string {
  const formatted = new Intl.NumberFormat('en-LK', {
    minimumFractionDigits: currencyConfig.decimalPlaces,
    maximumFractionDigits: currencyConfig.decimalPlaces,
  }).format(amount);
  return options?.hideSymbol ? formatted : `${currencyConfig.symbol} ${formatted}`;
}

// ─── Locale Config ───────────────────────────────────────────────────────────

export const localeConfig = {
  locale: 'en-LK',
  timezone: 'Asia/Colombo',
  dateFormat: 'DD/MM/YYYY',
  timeFormat: '24-hour' as const,
  phonePrefix: '+94',
  addressFormat: {
    fields: ['street', 'city', 'district', 'province', 'postalCode'] as const,
    postalCodeLength: 5,
    country: 'Sri Lanka',
    countryCode: 'LK',
  },
} as const;

/** Format a Date to Sri Lankan locale string */
export function formatDate(date: Date | string): string {
  return new Intl.DateTimeFormat('en-LK', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    timeZone: localeConfig.timezone,
  }).format(new Date(date));
}

/** Format a Date to time string */
export function formatTime(date: Date | string): string {
  return new Intl.DateTimeFormat('en-LK', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: localeConfig.timezone,
  }).format(new Date(date));
}

/** Validate a Sri Lankan phone number */
export function validatePhoneNumber(phone: string): boolean {
  const cleaned = phone.replace(/[\s-]/g, '');
  return /^(\+94|0)(7[0-9])[0-9]{7}$/.test(cleaned);
}

/** Format phone number to +94 format */
export function formatPhoneNumber(phone: string): string {
  const cleaned = phone.replace(/[\s-]/g, '');
  if (cleaned.startsWith('0')) {
    return `+94 ${cleaned.slice(1, 3)} ${cleaned.slice(3, 6)} ${cleaned.slice(6)}`;
  }
  if (cleaned.startsWith('+94')) {
    const digits = cleaned.slice(3);
    return `+94 ${digits.slice(0, 2)} ${digits.slice(2, 5)} ${digits.slice(5)}`;
  }
  return phone;
}

// ─── Feature Flags ───────────────────────────────────────────────────────────

export const featuresConfig = {
  customer: {
    wishlist: true,
    compare: true,
    reviews: true,
    questions: false,
    recentlyViewed: true,
  },
  checkout: {
    guestCheckout: true,
    expressCheckout: false,
    savedPayments: false,
    coupons: true,
  },
  account: {
    registration: true,
    socialLogin: false,
    newsletter: true,
    notifications: true,
  },
  shopping: {
    advancedSearch: true,
    autocomplete: true,
    filters: true,
    quickView: true,
  },
  social: {
    sharing: true,
    integration: false,
  },
  advanced: {
    pwa: false,
    liveChat: false,
    analytics: true,
  },
  payment: {
    multipleMethod: true,
    installments: false,
    cod: true,
    wallets: false,
    bankTransfer: true,
  },
  shipping: {
    multipleMethods: true,
    storePickup: false,
  },
} as const;

/** Check if a feature is enabled */
export function isFeatureEnabled(category: keyof typeof featuresConfig, feature: string): boolean {
  const cat = featuresConfig[category] as Record<string, boolean>;
  return cat?.[feature] ?? false;
}

// ─── Combined Config ─────────────────────────────────────────────────────────

export const storeConfig = {
  store: storeInfo,
  api: apiConfig,
  currency: currencyConfig,
  locale: localeConfig,
  features: featuresConfig,
} as const;

export type StoreConfig = typeof storeConfig;

/** Helper to get full API URL */
export function getApiUrl(path: string): string {
  const base = apiConfig.baseUrl.replace(/\/$/, '');
  return `${base}/${path.replace(/^\//, '')}`;
}

/** Helper to get full store URL */
export function getStoreUrl(path: string): string {
  const base = apiConfig.storeUrl.replace(/\/$/, '');
  return `${base}/${path.replace(/^\//, '')}`;
}
