export {
  storeConfig,
  storeInfo,
  apiConfig,
  currencyConfig,
  localeConfig,
  featuresConfig,
} from './config';
export {
  formatCurrency,
  formatDate,
  formatTime,
  formatPhoneNumber,
  validatePhoneNumber,
} from './config';
export { isFeatureEnabled, getApiUrl, getStoreUrl } from './config';
export type { StoreConfig } from './config';
export { storeRoutes, getRoute, generateBreadcrumbs } from './routes';
export { mainNavigation, footerNavigation, accountNavigation } from './navigation';
export type { NavItem } from './navigation';
export { socialLinks, getSocialUrl } from './social';
export type { SocialLink } from './social';

// Category utilities
export {
  getCategoryBySlug,
  getSubcategories,
  getCategoryBreadcrumbs,
  getCategoryTree,
} from './categories';

// Collection utilities
export {
  getCollectionBySlug,
  getRelatedCollections,
  getFeaturedCollections,
  getAllCollections,
  getCollectionBreadcrumbs,
} from './collections';
export type { StoreCollection, FeaturedCollection } from './collections';

// Store utilities
export * from './utils';
