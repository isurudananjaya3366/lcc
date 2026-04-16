/**
 * Storefront Types Barrel Export
 *
 * Central export point for all storefront type definitions.
 * Usage: import { StoreProduct, StoreCategory } from '@/types/store';
 */

// Product types
export { StoreProductStatus } from './product';
export type {
  StoreProduct,
  StoreProductVariant,
  StoreVariantOption,
  StoreProductImage,
  StoreProductAttribute,
  StoreProductFilters,
  StoreProductSort,
} from './product';

// Category types
export type {
  StoreCategory,
  StoreCategoryTree,
  StoreCategoryBreadcrumb,
  StoreCategoryFilters,
} from './category';

// Cart types
export type {
  StoreCartItem,
  StoreCart,
  StoreCartDiscount,
  StoreShippingMethod,
  StoreCartValidation,
} from './cart';

// Customer types
export { SriLankanProvince } from './customer';
export type {
  StoreCustomer,
  StoreCustomerAddress,
  StoreCustomerPreferences,
  StoreAuthTokens,
  StoreCustomerAuth,
} from './customer';

// Order types
export { StoreOrderStatus, StorePaymentMethodType } from './order';
export type {
  StoreOrder,
  StoreOrderItem,
  StorePaymentMethod,
  StorePaymentTransaction,
} from './order';

// Checkout types
export { StoreCheckoutStep } from './checkout';
export type {
  StoreCheckoutSession,
  StoreCheckoutValidation,
  StoreFieldValidation,
  StoreCheckoutSummary,
  StoreOrderConfirmation,
  StoreOrderReceipt,
} from './checkout';

// Common types
export { StoreLoadingState } from './common';
export type {
  StoreCurrency,
  StoreLocale,
  StorePagination,
  StoreSortOption,
  StoreFilterOption,
  StoreApiStatus,
  StoreErrorResponse,
  StoreSuccessResponse,
} from './common';

// API types
export { isStoreApiResponse, isValidEmail, isValidPhone, isValidPostalCode } from './api';
export type { StoreApiResponse, StorePaginatedResponse } from './api';

// Layout types
export type {
  StoreLayoutProps,
  AnnouncementBarConfig,
  AnnouncementBarState,
  LayoutScrollState,
  HeaderBehavior,
  LayoutAnimation,
  LayoutSection,
  LayoutTheme,
  ContainerMaxWidth,
  LayoutContainerProps,
  MainContentProps,
  UseStickyHeaderOptions,
  StickyHeaderState,
  ScrollPosition,
  UseScrollPositionOptions,
} from './layout';
