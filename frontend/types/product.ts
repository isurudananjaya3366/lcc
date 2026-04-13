/**
 * Product Types
 *
 * Comprehensive TypeScript types for products including product entities,
 * variants, pricing structures, stock tracking, and API request/response formats.
 */

// ── Enums ──────────────────────────────────────────────────────

export enum ProductStatus {
  DRAFT = 'DRAFT',
  ACTIVE = 'ACTIVE',
  DISCONTINUED = 'DISCONTINUED',
  OUT_OF_STOCK = 'OUT_OF_STOCK',
}

export enum ProductType {
  SIMPLE = 'SIMPLE',
  VARIABLE = 'VARIABLE',
  SERVICE = 'SERVICE',
  DIGITAL = 'DIGITAL',
}

export enum UnitOfMeasure {
  PIECE = 'PIECE',
  KG = 'KG',
  GRAM = 'GRAM',
  LITER = 'LITER',
  METER = 'METER',
  SQUARE_METER = 'SQUARE_METER',
}

// ── Supporting Interfaces ──────────────────────────────────────

export interface ProductVariant {
  id: string;
  productId: string;
  sku: string;
  variantName: string;
  attributeValues: Record<string, string>;
  price: number;
  compareAtPrice?: number;
  cost: number;
  stockQuantity: number;
  barcode?: string;
  weight?: number;
  dimensions?: { length: number; width: number; height: number };
  isActive: boolean;
}

export interface ProductAttribute {
  id: string;
  name: string;
  values: string[];
}

export interface ProductPricing {
  basePrice: number;
  compareAtPrice?: number;
  cost: number;
  margin: number;
  taxRate: number;
  taxInclusive: boolean;
  currencyCode: string;
  priceTiers?: { minQuantity: number; price: number }[];
}

export interface ProductInventory {
  trackInventory: boolean;
  stockQuantity: number;
  lowStockThreshold: number;
  allowBackorder: boolean;
  requiresSerial: boolean;
  warehouseAllocations?: { warehouseId: string; quantity: number }[];
}

export interface ProductImage {
  id: string;
  url: string;
  thumbnailUrl?: string;
  alt: string;
  position: number;
  isPrimary: boolean;
  size?: number;
  format?: string;
}

export interface ProductCategory {
  id: string;
  name: string;
  slug: string;
  description?: string;
  parentId?: string;
  imageUrl?: string;
  displayOrder: number;
  isActive: boolean;
  productCount: number;
  seoMetadata?: {
    title?: string;
    description?: string;
    keywords?: string[];
  };
}

export interface ProductBrand {
  id: string;
  name: string;
  slug: string;
  description?: string;
  logoUrl?: string;
  website?: string;
  isActive: boolean;
  productCount: number;
}

// ── Main Entity ────────────────────────────────────────────────

export interface Product {
  id: string;
  tenantId: string;
  sku: string;
  barcode?: string;
  name: string;
  description?: string;
  productType: ProductType;
  status: ProductStatus;
  categoryId?: string;
  brandId?: string;
  unitOfMeasure: UnitOfMeasure;
  pricing: ProductPricing;
  inventory: ProductInventory;
  variants?: ProductVariant[];
  attributes?: ProductAttribute[];
  images?: ProductImage[];
  tags?: string[];
  customFields?: Record<string, unknown>;
  seoMetadata?: {
    title?: string;
    description?: string;
    keywords?: string[];
  };
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  createdBy?: string;
}

// ── API Request/Response Interfaces ────────────────────────────

export interface ProductCreateRequest {
  sku: string;
  barcode?: string;
  name: string;
  description?: string;
  productType: ProductType;
  status?: ProductStatus;
  categoryId?: string;
  brandId?: string;
  unitOfMeasure: UnitOfMeasure;
  pricing: Omit<ProductPricing, 'margin'>;
  inventory?: Partial<ProductInventory>;
  variants?: Omit<ProductVariant, 'id' | 'productId'>[];
  attributes?: Omit<ProductAttribute, 'id'>[];
  images?: File[];
  tags?: string[];
  customFields?: Record<string, unknown>;
}

export interface ProductUpdateRequest {
  sku?: string;
  barcode?: string;
  name?: string;
  description?: string;
  productType?: ProductType;
  status?: ProductStatus;
  categoryId?: string;
  brandId?: string;
  unitOfMeasure?: UnitOfMeasure;
  pricing?: Partial<ProductPricing>;
  inventory?: Partial<ProductInventory>;
  tags?: string[];
  customFields?: Record<string, unknown>;
}

export interface ProductSearchParams {
  query?: string;
  categoryId?: string;
  brandId?: string;
  status?: ProductStatus;
  productType?: ProductType;
  priceMin?: number;
  priceMax?: number;
  inStock?: boolean;
  tags?: string[];
  sort?: string;
  page?: number;
  pageSize?: number;
}

export interface ProductBulkOperation {
  productIds: string[];
  operation: 'update' | 'delete' | 'activate' | 'deactivate';
  changes?: Partial<ProductUpdateRequest>;
}

export interface ProductImportRow {
  sku: string;
  name: string;
  description?: string;
  price: number;
  cost?: number;
  quantity?: number;
  categoryName?: string;
  brandName?: string;
  validationStatus: 'valid' | 'warning' | 'error';
  errors?: string[];
}
