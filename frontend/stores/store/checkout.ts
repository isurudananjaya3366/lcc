'use client';

import { createStore } from '../utils';
import type {
  CheckoutState,
  CheckoutStep,
  ContactInfo,
  ShippingAddress,
  ShippingMethod,
  PaymentMethodType,
  PaymentDetails,
  OrderInfo,
} from '@/types/storefront/checkout.types';

// ─── Types ──────────────────────────────────────────────────────────────────

interface CheckoutStoreState extends CheckoutState {
  // Actions
  setContactInfo: (info: Partial<ContactInfo>) => void;
  setShippingAddress: (address: Partial<ShippingAddress>) => void;
  setShippingMethod: (method: ShippingMethod) => void;
  setPaymentMethod: (method: PaymentMethodType) => void;
  setPaymentDetails: (details: PaymentDetails) => void;
  setOrderInfo: (info: OrderInfo) => void;
  setCurrentStep: (step: CheckoutStep) => void;
  completeStep: (step: CheckoutStep) => void;
  setIsProcessing: (processing: boolean) => void;
  reset: () => void;
}

// ─── Initial State ──────────────────────────────────────────────────────────

const initialContactInfo: ContactInfo = {
  email: '',
  phone: '',
  firstName: '',
  lastName: '',
  whatsappOptIn: false,
};

const initialShippingAddress: ShippingAddress = {
  province: '',
  district: '',
  city: '',
  address1: '',
  address2: '',
  landmark: '',
  postalCode: '',
};

const initialState: Omit<CheckoutStoreState, 'setContactInfo' | 'setShippingAddress' | 'setShippingMethod' | 'setPaymentMethod' | 'setPaymentDetails' | 'setOrderInfo' | 'setCurrentStep' | 'completeStep' | 'setIsProcessing' | 'reset'> = {
  currentStep: 1 as CheckoutStep,
  completedSteps: [],
  contactInfo: initialContactInfo,
  shippingAddress: initialShippingAddress,
  shippingMethod: null,
  paymentMethod: null,
  paymentDetails: null,
  orderInfo: null,
  isProcessing: false,
};

// ─── Store ──────────────────────────────────────────────────────────────────

export const useStoreCheckoutStore = createStore<CheckoutStoreState>(
  'StoreCheckout',
  (set) => ({
    ...initialState,

    setContactInfo: (info) => {
      set((state) => {
        Object.assign(state.contactInfo, info);
      });
    },

    setShippingAddress: (address) => {
      set((state) => {
        Object.assign(state.shippingAddress, address);
      });
    },

    setShippingMethod: (method) => {
      set((state) => {
        state.shippingMethod = method;
      });
    },

    setPaymentMethod: (method) => {
      set((state) => {
        state.paymentMethod = method;
      });
    },

    setPaymentDetails: (details) => {
      set((state) => {
        state.paymentDetails = details;
      });
    },

    setOrderInfo: (info) => {
      set((state) => {
        state.orderInfo = info;
      });
    },

    setCurrentStep: (step) => {
      set((state) => {
        state.currentStep = step;
      });
    },

    completeStep: (step) => {
      set((state) => {
        if (!state.completedSteps.includes(step)) {
          state.completedSteps.push(step);
        }
      });
    },

    setIsProcessing: (processing) => {
      set((state) => {
        state.isProcessing = processing;
      });
    },

    reset: () => {
      set((state) => {
        Object.assign(state, initialState);
      });
    },
  }),
  {
    persist: true,
    persistConfig: {
      name: 'lcc-store-checkout',
      version: 1,
      partialize: (state: CheckoutStoreState) => ({
        currentStep: state.currentStep,
        completedSteps: state.completedSteps,
        contactInfo: state.contactInfo,
        shippingAddress: state.shippingAddress,
        shippingMethod: state.shippingMethod,
        paymentMethod: state.paymentMethod,
        paymentDetails: state.paymentDetails,
        orderInfo: state.orderInfo,
      }),
    },
  }
);
