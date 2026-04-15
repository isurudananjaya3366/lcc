/**
 * Storefront Product Types
 *
 * Customer-facing product types for the webstore, distinct from
 * the ERP/admin product types in types/product.ts.
 */

// ─── Enums ───────────────────────────────────────────────────────────────────

export enum StoreProductStatus {
  ACTIVE = 'active',
  DRAFT = 'draft',
  ARCHIVED = 'archived',
  OUT_OF_STOCK = 'out_of_stock',
}

// ─── Core Interfaces ─────────────────────────────────────────────────────────

export interface StoreProduct {
  id: string;
  name: string;
  slug: string;
  description: string;
  shortDescription?: string;
  sku: string;
  price: number;
  compareAtPrice?: number;
  currency: string;
  status: StoreProductStatus;
  categoryId: string;
  categoryName: string;
  categorySlug: string;
  images: StoreProductImage[];
  variants: StoreProductVariant[];
  attributes: StoreProductAttribute[];
  stockQuantity: number;
  allowBackorder: boolean;
  isFeatured: boolean;
  isOnSale: boolean;
  tags: string[];
  rating: number;
  reviewCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface StoreProductVariant {
  id: string;
  name: string;
  sku: string;
  price: number;
  compareAtPrice?: number;
  stockQuantity: number;
  options: StoreVariantOption[];
  isAvailable: boolean;
  image?: StoreProductImage;
}

export interface StoreVariantOption {
  name: string;
  value: string;
}

export interface StoreProductImage {
  id: string;
  url: string;
  altText?: string;
  isPrimary: boolean;
  sortOrder: number;
}

export interface StoreProductAttribute {
  name: string;
  values: string[];
}

// ─── Filters & Sorting ──────────────────────────────────────────────────────

export interface StoreProductFilters {
  category?: string;
  minPrice?: number;
  maxPrice?: number;
  search?: string;
  tags?: string[];
  inStock?: boolean;
  onSale?: boolean;
  featured?: boolean;
  sort?: StoreProductSort;
  page?: number;
  pageSize?: number;
}

export type StoreProductSort =
  | 'name_asc'
  | 'name_desc'
  | 'price_asc'
  | 'price_desc'
  | 'newest'
  | 'oldest'
  | 'rating'
  | 'popularity';
