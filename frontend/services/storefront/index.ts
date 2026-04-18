export { searchProducts, searchCategories, getSearchSuggestions } from './searchService';

export type { SearchProduct, SearchCategory, SearchSuggestionsResult } from './searchService';

export { validateCoupon } from './couponService';
export type { CouponValidationResult } from './couponService';

export {
  syncCartToServer,
  fetchServerCart,
  mergeGuestCart,
  validateCartStock,
} from './cartService';
export type { CartSyncItem, ServerCartItem, StockValidationResult } from './cartService';

export { submitOrder, getOrderStatus, cartItemsToOrderLines } from './orderService';
export type {
  OrderSubmitPayload,
  OrderConfirmation,
  OrderStatus,
  OrderLineItem,
} from './orderService';

export {
  loginApi,
  registerApi,
  logoutApi,
  getCurrentUser,
  requestPasswordReset,
  verifyOTP,
  resetPassword,
  refreshTokenApi,
} from './authService';

export {
  getAccessToken,
  setAccessToken,
  getRefreshToken,
  setRefreshToken,
  clearTokens,
  isTokenExpired,
  getTokenExpiryMs,
  getRememberMe,
  setRememberMe,
} from './tokenService';
