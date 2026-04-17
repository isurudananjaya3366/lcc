/**
 * Enhanced cart types for the storefront.
 */

export interface CartItemVariant {
  name: string; // e.g. "Size"
  value: string; // e.g. "M"
}

export interface StorefrontCartItem {
  id: string;
  productId: string;
  productSlug: string;
  name: string;
  sku: string;
  price: number;
  compareAtPrice?: number;
  quantity: number;
  maxQuantity: number;
  imageUrl: string;
  variants: CartItemVariant[];
  variantKey: string;
}

export interface CouponDiscount {
  code: string;
  type: 'percentage' | 'fixed';
  value: number;
  description: string;
}

export interface CartSummary {
  itemCount: number;
  subtotal: number;
  discount: number;
  shipping: number | null; // null = calculated at checkout
  tax: number;
  total: number;
}
