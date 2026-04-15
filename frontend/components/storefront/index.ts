/**
 * Storefront Components
 *
 * Barrel file exporting all storefront-specific components.
 */

// Layout components
export { StoreLayout, StoreHeader, StoreFooter, StoreNavigation } from './layout';
export {
  generateStoreMetadata,
  productMetadata,
  categoryMetadata,
  pageMetadata,
} from './layout/StoreHead';

// Provider components
export {
  StoreProviders,
  ThemeProvider,
  useStoreTheme,
  CartProvider,
  useCart,
  AuthProvider,
  useStoreAuth,
} from './providers';

// Product components (SubPhase-03)
// export { ProductCard } from './product/ProductCard';
// export { ProductGrid } from './product/ProductGrid';

// Cart components (SubPhase-06)
// export { CartDrawer } from './cart/CartDrawer';

// Search components (SubPhase-05)
// export { SearchBar } from './search/SearchBar';
