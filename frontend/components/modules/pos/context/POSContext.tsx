'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useReducer,
  type ReactNode,
} from 'react';
import type {
  POSCartItem,
  POSContextType,
  POSCustomer,
  POSDiscount,
  POSModalType,
  POSSale,
  POSShift,
  POSState,
} from '../types';

// ── Initial State ──────────────────────────────────────────────

const initialState: POSState = {
  cartItems: [],
  currentShift: null,
  customer: null,
  cartDiscount: null,
  activeModal: null,
  isLoading: false,
  heldSales: [],
};

// ── Reducer ────────────────────────────────────────────────────

type POSAction =
  | { type: 'ADD_TO_CART'; payload: POSCartItem }
  | { type: 'UPDATE_QUANTITY'; payload: { itemId: string; quantity: number } }
  | { type: 'REMOVE_FROM_CART'; payload: string }
  | { type: 'CLEAR_CART' }
  | { type: 'APPLY_ITEM_DISCOUNT'; payload: { itemId: string; discount: POSDiscount } }
  | { type: 'REMOVE_ITEM_DISCOUNT'; payload: string }
  | { type: 'APPLY_CART_DISCOUNT'; payload: POSDiscount }
  | { type: 'REMOVE_CART_DISCOUNT' }
  | { type: 'SET_CUSTOMER'; payload: POSCustomer | null }
  | { type: 'SET_SHIFT'; payload: POSShift | null }
  | { type: 'OPEN_MODAL'; payload: POSModalType }
  | { type: 'CLOSE_MODAL' }
  | { type: 'HOLD_SALE'; payload: POSSale }
  | { type: 'RETRIEVE_HELD_SALE'; payload: string }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'RESTORE_STATE'; payload: Partial<POSState> };

function calculateLineTotal(item: POSCartItem): POSCartItem {
  const subtotal = item.quantity * item.unitPrice;
  let discountAmount = 0;
  if (item.discount) {
    discountAmount =
      item.discount.type === 'percentage'
        ? subtotal * (item.discount.value / 100)
        : Math.min(item.discount.value, subtotal);
  }
  const afterDiscount = subtotal - discountAmount;
  const taxAmount = item.isTaxable ? afterDiscount * (item.taxRate / 100) : 0;
  return {
    ...item,
    discountAmount,
    taxAmount,
    lineTotal: afterDiscount + taxAmount,
  };
}

function posReducer(state: POSState, action: POSAction): POSState {
  switch (action.type) {
    case 'ADD_TO_CART': {
      const existing = state.cartItems.find(
        (i) => i.productId === action.payload.productId && i.variantId === action.payload.variantId
      );
      if (existing) {
        return {
          ...state,
          cartItems: state.cartItems.map((item) =>
            item.id === existing.id
              ? calculateLineTotal({ ...item, quantity: item.quantity + action.payload.quantity })
              : item
          ),
        };
      }
      return {
        ...state,
        cartItems: [...state.cartItems, calculateLineTotal(action.payload)],
      };
    }

    case 'UPDATE_QUANTITY': {
      if (action.payload.quantity <= 0) {
        return {
          ...state,
          cartItems: state.cartItems.filter((i) => i.id !== action.payload.itemId),
        };
      }
      return {
        ...state,
        cartItems: state.cartItems.map((item) =>
          item.id === action.payload.itemId
            ? calculateLineTotal({ ...item, quantity: action.payload.quantity })
            : item
        ),
      };
    }

    case 'REMOVE_FROM_CART':
      return {
        ...state,
        cartItems: state.cartItems.filter((i) => i.id !== action.payload),
      };

    case 'CLEAR_CART':
      return {
        ...state,
        cartItems: [],
        customer: null,
        cartDiscount: null,
      };

    case 'APPLY_ITEM_DISCOUNT':
      return {
        ...state,
        cartItems: state.cartItems.map((item) =>
          item.id === action.payload.itemId
            ? calculateLineTotal({ ...item, discount: action.payload.discount })
            : item
        ),
      };

    case 'REMOVE_ITEM_DISCOUNT':
      return {
        ...state,
        cartItems: state.cartItems.map((item) =>
          item.id === action.payload ? calculateLineTotal({ ...item, discount: undefined }) : item
        ),
      };

    case 'APPLY_CART_DISCOUNT':
      return { ...state, cartDiscount: action.payload };

    case 'REMOVE_CART_DISCOUNT':
      return { ...state, cartDiscount: null };

    case 'SET_CUSTOMER':
      return { ...state, customer: action.payload };

    case 'SET_SHIFT':
      return { ...state, currentShift: action.payload };

    case 'OPEN_MODAL':
      return { ...state, activeModal: action.payload };

    case 'CLOSE_MODAL':
      return { ...state, activeModal: null };

    case 'HOLD_SALE':
      return {
        ...state,
        heldSales: [...state.heldSales, action.payload],
        cartItems: [],
        customer: null,
        cartDiscount: null,
      };

    case 'RETRIEVE_HELD_SALE': {
      const sale = state.heldSales.find((s) => s.id === action.payload);
      if (!sale) return state;
      return {
        ...state,
        heldSales: state.heldSales.filter((s) => s.id !== action.payload),
        cartItems: sale.items,
        customer: sale.customer ?? null,
        cartDiscount: sale.discount ?? null,
      };
    }

    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };

    case 'RESTORE_STATE':
      return { ...state, ...action.payload };

    default:
      return state;
  }
}

// ── Context ────────────────────────────────────────────────────

const POSContext = createContext<POSContextType | undefined>(undefined);

const STORAGE_KEY = 'lcc-pos-cart';

// ── Provider ───────────────────────────────────────────────────

export function POSProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(posReducer, initialState);

  // Restore cart from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved) as Partial<POSState>;
        dispatch({
          type: 'RESTORE_STATE',
          payload: { cartItems: parsed.cartItems ?? [], heldSales: parsed.heldSales ?? [] },
        });
      }
    } catch {
      // Ignore invalid data
    }
  }, []);

  // Persist cart to localStorage on changes
  useEffect(() => {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ cartItems: state.cartItems, heldSales: state.heldSales })
      );
    } catch {
      // Storage full or unavailable
    }
  }, [state.cartItems, state.heldSales]);

  // ── Actions ────────────────────────────────────────────

  const addToCart = useCallback(
    (item: Omit<POSCartItem, 'id' | 'addedAt' | 'lineTotal' | 'discountAmount' | 'taxAmount'>) => {
      const cartItem: POSCartItem = {
        ...item,
        id: `${item.productId}-${item.variantId ?? 'base'}-${Date.now()}`,
        addedAt: new Date().toISOString(),
        lineTotal: 0,
        discountAmount: 0,
        taxAmount: 0,
      };
      dispatch({ type: 'ADD_TO_CART', payload: cartItem });
    },
    []
  );

  const updateQuantity = useCallback((itemId: string, quantity: number) => {
    dispatch({ type: 'UPDATE_QUANTITY', payload: { itemId, quantity } });
  }, []);

  const removeFromCart = useCallback((itemId: string) => {
    dispatch({ type: 'REMOVE_FROM_CART', payload: itemId });
  }, []);

  const clearCart = useCallback(() => {
    dispatch({ type: 'CLEAR_CART' });
  }, []);

  const applyItemDiscount = useCallback((itemId: string, discount: POSDiscount) => {
    dispatch({ type: 'APPLY_ITEM_DISCOUNT', payload: { itemId, discount } });
  }, []);

  const removeItemDiscount = useCallback((itemId: string) => {
    dispatch({ type: 'REMOVE_ITEM_DISCOUNT', payload: itemId });
  }, []);

  const applyCartDiscount = useCallback((discount: POSDiscount) => {
    dispatch({ type: 'APPLY_CART_DISCOUNT', payload: discount });
  }, []);

  const removeCartDiscount = useCallback(() => {
    dispatch({ type: 'REMOVE_CART_DISCOUNT' });
  }, []);

  const setCustomer = useCallback((customer: POSCustomer | null) => {
    dispatch({ type: 'SET_CUSTOMER', payload: customer });
  }, []);

  const setShift = useCallback((shift: POSShift | null) => {
    dispatch({ type: 'SET_SHIFT', payload: shift });
  }, []);

  const openModal = useCallback((modal: POSModalType) => {
    dispatch({ type: 'OPEN_MODAL', payload: modal });
  }, []);

  const closeModal = useCallback(() => {
    dispatch({ type: 'CLOSE_MODAL' });
  }, []);

  const holdSale = useCallback(
    (reason?: string) => {
      if (state.cartItems.length === 0) return;
      const sale: POSSale = {
        id: `hold-${Date.now()}`,
        referenceNumber: `HOLD-${Date.now()}`,
        items: state.cartItems,
        customer: state.customer ?? undefined,
        discount: state.cartDiscount ?? undefined,
        payments: [],
        subtotal: state.cartItems.reduce((sum, i) => sum + i.quantity * i.unitPrice, 0),
        discountAmount: 0,
        taxAmount: 0,
        grandTotal: 0,
        status: 'held',
        heldReason: reason,
        createdAt: new Date().toISOString(),
      };
      dispatch({ type: 'HOLD_SALE', payload: sale });
    },
    [state.cartItems, state.customer, state.cartDiscount]
  );

  const retrieveHeldSale = useCallback((saleId: string) => {
    dispatch({ type: 'RETRIEVE_HELD_SALE', payload: saleId });
  }, []);

  // ── Computed ───────────────────────────────────────────

  const getSubtotal = useCallback(() => {
    return state.cartItems.reduce((sum, item) => sum + item.quantity * item.unitPrice, 0);
  }, [state.cartItems]);

  const getDiscountTotal = useCallback(() => {
    let itemDiscounts = state.cartItems.reduce((sum, item) => sum + item.discountAmount, 0);
    if (state.cartDiscount) {
      const subtotal = getSubtotal();
      const cartDiscountAmt =
        state.cartDiscount.type === 'percentage'
          ? subtotal * (state.cartDiscount.value / 100)
          : Math.min(state.cartDiscount.value, subtotal);
      itemDiscounts += cartDiscountAmt;
    }
    return itemDiscounts;
  }, [state.cartItems, state.cartDiscount, getSubtotal]);

  const getTaxTotal = useCallback(() => {
    return state.cartItems.reduce((sum, item) => sum + item.taxAmount, 0);
  }, [state.cartItems]);

  const getGrandTotal = useCallback(() => {
    const subtotal = getSubtotal();
    const discount = getDiscountTotal();
    const tax = getTaxTotal();
    return subtotal - discount + tax;
  }, [getSubtotal, getDiscountTotal, getTaxTotal]);

  const getItemCount = useCallback(() => {
    return state.cartItems.reduce((sum, item) => sum + item.quantity, 0);
  }, [state.cartItems]);

  // ── Context Value ──────────────────────────────────────

  const value = useMemo<POSContextType>(
    () => ({
      ...state,
      addToCart,
      updateQuantity,
      removeFromCart,
      clearCart,
      applyItemDiscount,
      removeItemDiscount,
      applyCartDiscount,
      removeCartDiscount,
      setCustomer,
      setShift,
      openModal,
      closeModal,
      holdSale,
      retrieveHeldSale,
      getSubtotal,
      getDiscountTotal,
      getTaxTotal,
      getGrandTotal,
      getItemCount,
    }),
    [
      state,
      addToCart,
      updateQuantity,
      removeFromCart,
      clearCart,
      applyItemDiscount,
      removeItemDiscount,
      applyCartDiscount,
      removeCartDiscount,
      setCustomer,
      setShift,
      openModal,
      closeModal,
      holdSale,
      retrieveHeldSale,
      getSubtotal,
      getDiscountTotal,
      getTaxTotal,
      getGrandTotal,
      getItemCount,
    ]
  );

  return <POSContext.Provider value={value}>{children}</POSContext.Provider>;
}

// ── Hook ───────────────────────────────────────────────────────

export function usePOS(): POSContextType {
  const context = useContext(POSContext);
  if (!context) {
    throw new Error('usePOS must be used within a POSProvider');
  }
  return context;
}
