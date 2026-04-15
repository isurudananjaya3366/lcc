/**
 * Store Utilities Barrel Export
 *
 * Re-exports all storefront utility functions and types.
 */

// Currency
export {
  formatCurrency,
  formatLKR,
  formatCompactCurrency,
  parseCurrency,
  formatCurrencyRange,
  convertCurrency,
} from './currency';

// Price display
export {
  displayPrice,
  formatPriceRange,
  getDiscountBadge,
  formatStrikethroughPrice,
  getPriceSummary,
} from './price';
export type { PriceDisplay } from './price';

// Discounts
export {
  DiscountType,
  calculatePercentageDiscount,
  calculateFixedDiscount,
  calculateDiscountPercentage,
  calculateSaveAmount,
  applyDiscount,
  calculateBulkDiscount,
  calculateBuyXGetY,
  calculateStackedDiscounts,
  isValidPercentage,
  isValidFixedDiscount,
} from './discount';
export type { DiscountResult, BulkTier } from './discount';

// Images
export {
  getImageUrl,
  getImageSrcSet,
  getPlaceholderImage,
  optimizeImageUrl,
  isValidImageUrl,
  getProductMainImage,
  getProductGallery,
  getProductThumbnail,
} from './images';
export type { ImageSize } from './images';

// URLs
export {
  getProductUrl,
  getProductsUrl,
  getCanonicalProductUrl,
  getProductVariantUrl,
  parseProductUrl,
  getCategoryUrl,
  getCategoryProductsUrl,
  getCategoriesUrl,
  getCanonicalCategoryUrl,
  parseCategoryUrl,
  getBreadcrumbs,
  generateSlug,
  getCartUrl,
  getCheckoutUrl,
  getAccountUrl,
  getOrderUrl,
  getSearchUrl,
} from './urls';
export type { BreadcrumbItem } from './urls';

// Cart calculations
export {
  calculateItemTotal,
  calculateSubtotal,
  calculateTax,
  calculateShipping,
  calculateDiscount,
  calculateTotal,
  getCartSummary,
  validateCartPrices,
  checkMinimumOrder,
  detectStockChanges,
} from './cart';
export type { CartCalcItem, CartSummary, CartValidation } from './cart';

// Stock
export {
  isInStock,
  getStockLevel,
  getStockStatus,
  getStockMessage,
  getStockInfo,
  canAddToCart,
  getAvailableQuantity,
} from './stock';
export type { StockStatus, StockInfo } from './stock';
