/** Cart item in the shopping cart */
export interface CartItem {
  id: string;
  productId: string;
  variantId?: string;
  name: string;
  price: number;
  quantity: number;
  imageUrl: string;
  maxQuantity?: number;
  metadata?: Record<string, unknown>;
}

/** Cart totals */
export interface CartTotals {
  subtotal: number;
  discount: number;
  tax: number;
  total: number;
}

/** Discount code applied to cart */
export interface DiscountCode {
  code: string;
  type: 'percentage' | 'fixed';
  value: number;
}

/** Full cart state */
export interface Cart {
  items: CartItem[];
  totals: CartTotals;
  discount?: DiscountCode;
  updatedAt: Date;
}

/** Cart context value exposed via useCart */
export interface CartContextValue {
  cart: Cart;
  itemCount: number;
  isLoading: boolean;
  addToCart: (item: CartItem) => void;
  removeFromCart: (itemId: string) => void;
  updateQuantity: (itemId: string, quantity: number) => void;
  clearCart: () => void;
  isInCart: (productId: string, variantId?: string) => boolean;
  applyDiscount: (discount: DiscountCode) => void;
  removeDiscount: () => void;
}

/** Cart reducer action types */
export type CartAction =
  | { type: 'ADD_ITEM'; payload: CartItem }
  | { type: 'REMOVE_ITEM'; payload: string }
  | { type: 'UPDATE_QUANTITY'; payload: { itemId: string; quantity: number } }
  | { type: 'CLEAR' }
  | { type: 'SET_CART'; payload: Cart }
  | { type: 'APPLY_DISCOUNT'; payload: DiscountCode }
  | { type: 'REMOVE_DISCOUNT' };
