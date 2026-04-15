// Store API Client - Main Export
export {
  getStoreClient,
  isConfigured,
  updateBaseURL,
  resetStoreClient,
  checkClientHealth,
} from './client';
export type {
  ApiResponse,
  PaginatedResponse,
  ApiError,
  ValidationError,
  ClientConfig,
} from './client';

// Configuration
export {
  detectEnvironment,
  loadEnvironmentConfig,
  normalizeUrl,
  buildApiUrl,
  validateUrl,
  getApiPrefix,
} from './config';
export type { EnvironmentConfig, UrlValidationResult } from './config';

// Interceptors
export type {
  JwtPayload,
  TokenStorage,
  TransformedError,
  RetryConfig,
  ApiErrorResponse,
} from './interceptors';

// API Modules
export {
  productsApi,
  categoriesApi,
  cartApi,
  checkoutApi,
  customerApi,
  ordersApi,
  reviewsApi,
  wishlistApi,
  searchApi,
} from './modules';

// Re-export all types from modules
export type {
  Product,
  ProductImage,
  ProductVariant,
  ProductReview,
  ProductsListParams,
  Category,
  CategoryTree,
  CategoriesListParams,
  StoreCart,
  StoreCartItem,
  AddToCartParams,
  UpdateCartItemParams,
  ApplyCouponParams,
  Checkout,
  ShippingAddress,
  PaymentMethod,
  ShippingMethod,
  OrderSummary,
  CheckoutStep,
  CheckoutProgress,
  Customer,
  CustomerAddress,
  CustomerPreferences,
  NotificationSettings,
  UserProfile,
  UpdateProfileParams,
  AddAddressParams,
  Order,
  OrderItem,
  OrderStatus,
  PaymentStatus,
  OrderTracking,
  OrdersListParams,
  ReturnRequestParams,
  Review,
  ReviewStats,
  ReviewAuthor,
  CreateReviewParams,
  UpdateReviewParams,
  ReviewsListParams,
  Wishlist,
  WishlistItem,
  WishlistSummary,
  SearchResult,
  SearchFilters,
  SearchFacet,
  SearchSuggestion,
  SearchHistoryItem,
} from './modules';
