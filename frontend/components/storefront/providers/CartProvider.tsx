'use client';

import React, {
  createContext,
  useContext,
  useReducer,
  useEffect,
  useCallback,
  type ReactNode,
  type FC,
} from 'react';
import type { Cart, CartItem, CartContextValue, CartAction, DiscountCode } from '@/types/cart';

const STORAGE_KEY = 'store-cart';

function calculateTotals(items: CartItem[], discount?: DiscountCode) {
  const subtotal = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  let discountAmount = 0;
  if (discount) {
    discountAmount =
      discount.type === 'percentage'
        ? Math.round(((subtotal * Math.min(100, discount.value)) / 100) * 100) / 100
        : Math.min(subtotal, discount.value);
  }
  const afterDiscount = subtotal - discountAmount;
  const tax = Math.round(afterDiscount * 0.08 * 100) / 100; // 8% VAT
  return { subtotal, discount: discountAmount, tax, total: afterDiscount + tax };
}

function cartReducer(state: Cart, action: CartAction): Cart {
  switch (action.type) {
    case 'ADD_ITEM': {
      const existing = state.items.find(
        (i) => i.productId === action.payload.productId && i.variantId === action.payload.variantId
      );
      let items: CartItem[];
      if (existing) {
        items = state.items.map((i) =>
          i.id === existing.id ? { ...i, quantity: i.quantity + (action.payload.quantity ?? 1) } : i
        );
      } else {
        items = [...state.items, { ...action.payload, quantity: action.payload.quantity ?? 1 }];
      }
      return {
        ...state,
        items,
        totals: calculateTotals(items, state.discount),
        updatedAt: new Date(),
      };
    }
    case 'REMOVE_ITEM': {
      const items = state.items.filter((i) => i.id !== action.payload);
      return {
        ...state,
        items,
        totals: calculateTotals(items, state.discount),
        updatedAt: new Date(),
      };
    }
    case 'UPDATE_QUANTITY': {
      const items = state.items.map((i) =>
        i.id === action.payload.itemId
          ? { ...i, quantity: Math.max(1, action.payload.quantity) }
          : i
      );
      return {
        ...state,
        items,
        totals: calculateTotals(items, state.discount),
        updatedAt: new Date(),
      };
    }
    case 'APPLY_DISCOUNT': {
      return {
        ...state,
        discount: action.payload,
        totals: calculateTotals(state.items, action.payload),
        updatedAt: new Date(),
      };
    }
    case 'REMOVE_DISCOUNT': {
      return {
        ...state,
        discount: undefined,
        totals: calculateTotals(state.items),
        updatedAt: new Date(),
      };
    }
    case 'CLEAR': {
      return {
        ...state,
        items: [],
        totals: calculateTotals([]),
        discount: undefined,
        updatedAt: new Date(),
      };
    }
    case 'SET_CART': {
      return {
        ...action.payload,
        totals: calculateTotals(action.payload.items, action.payload.discount),
      };
    }
    default:
      return state;
  }
}

const initialCart: Cart = {
  items: [],
  totals: { subtotal: 0, discount: 0, tax: 0, total: 0 },
  updatedAt: new Date(),
};

const CartContext = createContext<CartContextValue | null>(null);

export interface CartProviderProps {
  children: ReactNode;
  storageKey?: string;
}

/**
 * Cart provider — manages shopping cart state with localStorage persistence
 * and cross-tab synchronization.
 */
const CartProvider: FC<CartProviderProps> = ({ children, storageKey = STORAGE_KEY }) => {
  const [cart, dispatch] = useReducer(cartReducer, initialCart);

  // Hydrate from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed?.items && Array.isArray(parsed.items)) {
          dispatch({ type: 'SET_CART', payload: parsed });
        }
      }
    } catch {
      // Ignore parse errors
    }
  }, [storageKey]);

  // Persist to localStorage on change
  useEffect(() => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(cart));
    } catch {
      // localStorage quota exceeded
    }
  }, [cart, storageKey]);

  // Cross-tab synchronization
  useEffect(() => {
    const handler = (e: StorageEvent) => {
      if (e.key === storageKey && e.newValue) {
        try {
          const parsed = JSON.parse(e.newValue);
          if (parsed?.items && Array.isArray(parsed.items)) {
            dispatch({ type: 'SET_CART', payload: parsed });
          }
        } catch {
          // Ignore
        }
      }
    };
    window.addEventListener('storage', handler);
    return () => window.removeEventListener('storage', handler);
  }, [storageKey]);

  const addToCart = useCallback((item: CartItem) => {
    dispatch({ type: 'ADD_ITEM', payload: item });
  }, []);

  const removeFromCart = useCallback((itemId: string) => {
    dispatch({ type: 'REMOVE_ITEM', payload: itemId });
  }, []);

  const updateQuantity = useCallback((itemId: string, quantity: number) => {
    dispatch({ type: 'UPDATE_QUANTITY', payload: { itemId, quantity } });
  }, []);

  const clearCart = useCallback(() => {
    dispatch({ type: 'CLEAR' });
  }, []);

  const applyDiscount = useCallback((discount: DiscountCode) => {
    dispatch({ type: 'APPLY_DISCOUNT', payload: discount });
  }, []);

  const removeDiscount = useCallback(() => {
    dispatch({ type: 'REMOVE_DISCOUNT' });
  }, []);

  const itemCount = cart.items.reduce((sum, i) => sum + i.quantity, 0);
  const isInCart = useCallback(
    (productId: string, variantId?: string) =>
      cart.items.some((i) => i.productId === productId && i.variantId === variantId),
    [cart.items]
  );

  const value: CartContextValue = {
    cart,
    itemCount,
    isLoading: false,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    isInCart,
    applyDiscount,
    removeDiscount,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};

export function useCart(): CartContextValue {
  const ctx = useContext(CartContext);
  if (!ctx) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return ctx;
}

export default CartProvider;
