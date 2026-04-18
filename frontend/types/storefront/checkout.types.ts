/**
 * Checkout Flow Types
 * SubPhase-07 Group A - Task 10
 */

export enum CheckoutStep {
  INFORMATION = 1,
  SHIPPING = 2,
  PAYMENT = 3,
  REVIEW = 4,
  CONFIRMATION = 5,
}

export interface ContactInfo {
  email: string;
  phone: string;
  firstName: string;
  lastName: string;
  whatsappOptIn: boolean;
}

export interface ShippingAddress {
  province: string;
  district: string;
  city: string;
  address1: string;
  address2: string;
  landmark: string;
  postalCode: string;
}

export interface ShippingMethod {
  id: string;
  name: string;
  description: string;
  price: number;
  estimatedDays: number;
  carrier: string;
}

export type PaymentMethodType =
  | 'payhere'
  | 'card'
  | 'bank_transfer'
  | 'cod'
  | 'koko'
  | 'mintpay';

export interface PaymentDetails {
  methodType: PaymentMethodType;
  bankReceipt?: string;
  transactionId?: string;
  cardLast4?: string;
}

export interface OrderInfo {
  orderId: string;
  orderNumber: string;
  status: string;
}

export interface CheckoutState {
  currentStep: CheckoutStep;
  completedSteps: CheckoutStep[];
  contactInfo: ContactInfo;
  shippingAddress: ShippingAddress;
  shippingMethod: ShippingMethod | null;
  paymentMethod: PaymentMethodType | null;
  paymentDetails: PaymentDetails | null;
  orderInfo: OrderInfo | null;
  isProcessing: boolean;
}

export interface StepValidation {
  isValid: boolean;
  errors: Record<string, string>;
}
