export { default as productsApi } from './products';
export { default as categoriesApi } from './categories';
export { default as cartApi } from './cart';
export { default as checkoutApi } from './checkout';
export { default as customerApi } from './customer';
export { default as ordersApi } from './orders';
export { default as reviewsApi } from './reviews';
export { default as wishlistApi } from './wishlist';
export { default as searchApi } from './search';

// Re-export types
export type {
  Product,
  ProductImage,
  ProductVariant,
  ProductReview,
  ProductsListParams,
} from './products';
export type { Category, CategoryTree, CategoriesListParams } from './categories';
export type {
  StoreCart,
  StoreCartItem,
  AddToCartParams,
  UpdateCartItemParams,
  ApplyCouponParams,
} from './cart';
export type {
  Checkout,
  ShippingAddress,
  PaymentMethod,
  ShippingMethod,
  OrderSummary,
  CheckoutStep,
  CheckoutProgress,
} from './checkout';
export type {
  Customer,
  CustomerAddress,
  CustomerPreferences,
  NotificationSettings,
  UserProfile,
  UpdateProfileParams,
  AddAddressParams,
} from './customer';
export type {
  Order,
  OrderItem,
  OrderStatus,
  PaymentStatus,
  OrderTracking,
  OrdersListParams,
  ReturnRequestParams,
} from './orders';
export type {
  Review,
  ReviewStats,
  ReviewAuthor,
  CreateReviewParams,
  UpdateReviewParams,
  ReviewsListParams,
} from './reviews';
export type { Wishlist, WishlistItem, WishlistSummary } from './wishlist';
export type {
  SearchResult,
  SearchFilters,
  SearchFacet,
  SearchSuggestion,
  SearchHistoryItem,
} from './search';
