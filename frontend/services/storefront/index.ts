export {
  searchProducts,
  searchCategories,
  getSearchSuggestions,
} from './searchService';

export type {
  SearchProduct,
  SearchCategory,
  SearchSuggestionsResult,
} from './searchService';

export { validateCoupon } from './couponService';
export type { CouponValidationResult } from './couponService';

export {
  syncCartToServer,
  fetchServerCart,
  mergeGuestCart,
  validateCartStock,
} from './cartService';
export type {
  CartSyncItem,
  ServerCartItem,
  StockValidationResult,
} from './cartService';
