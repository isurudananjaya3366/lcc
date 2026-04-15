/**
 * Storefront Cart Types
 */

export interface StoreCartItem {
  id: string;
  productId: string;
  variantId?: string;
  sku: string;
  name: string;
  slug: string;
  price: number;
  quantity: number;
  lineTotal: number;
  image: string;
  thumbnailUrl?: string;
  variantAttributes?: Array<{ name: string; value: string }>;
  maxQuantity: number;
  isAvailable: boolean;
}

export interface StoreCart {
  items: StoreCartItem[];
  itemCount: number;
  subtotal: number;
  discount: number;
  tax: number;
  shipping: number;
  total: number;
  currency: string;
  lastUpdated: string;
}

export interface StoreCartDiscount {
  code: string;
  type: 'percentage' | 'fixed';
  value: number;
  description: string;
  appliedAmount: number;
}

export interface StoreShippingMethod {
  id: string;
  name: string;
  price: number;
  estimatedDays: number;
  carrier: string;
}

export interface StoreCartValidation {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}
