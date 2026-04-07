// ================================================================
// Application Configuration Constants
// ================================================================
// All values use 'as const' for literal type inference.
// ================================================================

// ── App Metadata ───────────────────────────────────────────────

export const APP_CONFIG = {
  name: 'LankaCommerce Cloud',
  shortName: 'LCC',
  version: '0.1.0',
  description: 'Multi-tenant SaaS ERP for Sri Lankan SMEs',
} as const;

// ── API Configuration ──────────────────────────────────────────

export const API_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || '/api',
  timeout: 30_000, // 30 seconds
  retryAttempts: 3,
  retryDelay: 1_000, // 1 second
} as const;

// ── Authentication ─────────────────────────────────────────────

export const AUTH_CONFIG = {
  tokenKey: 'accessToken',
  refreshKey: 'refreshToken',
  expiryBuffer: 60, // seconds before expiry to trigger refresh
} as const;

// ── Pagination ─────────────────────────────────────────────────

export const PAGINATION = {
  defaultPageSize: 20,
  pageSizeOptions: [10, 20, 50, 100] as readonly number[],
  maxPageSize: 100,
} as const;

// ── Sri Lanka Configuration ────────────────────────────────────

export const SRI_LANKA = {
  currency: {
    code: 'LKR',
    symbol: '₨',
    name: 'Sri Lankan Rupee',
    decimals: 2,
  },
  timezone: 'Asia/Colombo',
  locale: 'en-LK',
  phonePrefix: '+94',
  phoneFormat: '+94 XX XXX XXXX',
  dateFormat: 'DD/MM/YYYY',
  timeFormat: 'HH:mm',
  countryCode: 'LK',
} as const;

// ── Feature Flags ──────────────────────────────────────────────

export const FEATURES = {
  darkMode: true,
  aiRecommendations: false,
  multiLanguage: true,
  smsNotifications: true,
  webstore: true,
  posSystem: true,
} as const;

// ── Type Exports ───────────────────────────────────────────────

export type AppConfig = typeof APP_CONFIG;
export type ApiConfig = typeof API_CONFIG;
export type SriLankaConfig = typeof SRI_LANKA;
export type FeatureFlags = typeof FEATURES;
