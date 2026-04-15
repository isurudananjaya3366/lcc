/**
 * Payment Methods Configuration
 *
 * Payment gateways, methods, limits, and settings.
 */

export interface PaymentMethod {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  icon?: string;
  minAmount: number;
  maxAmount: number;
  surcharge?: number;
}

export const paymentMethods: PaymentMethod[] = [
  {
    id: 'cod',
    name: 'Cash on Delivery',
    description: 'Pay with cash when your order is delivered',
    enabled: true,
    minAmount: 100,
    maxAmount: 50000,
    surcharge: 100,
  },
  {
    id: 'payhere',
    name: 'PayHere',
    description: 'Pay with local bank cards (Visa, Mastercard, AMEX, 3D Secure)',
    enabled: true,
    minAmount: 100,
    maxAmount: 500000,
  },
  {
    id: 'stripe',
    name: 'International Cards',
    description: 'Pay with international Visa or Mastercard via Stripe',
    enabled: false,
    minAmount: 100,
    maxAmount: 500000,
  },
  {
    id: 'bank_transfer',
    name: 'Bank Transfer',
    description: 'Direct transfer to our bank account',
    enabled: true,
    minAmount: 1000,
    maxAmount: 500000,
  },
];

export const bankAccounts = [
  {
    bank: 'Commercial Bank of Ceylon',
    branch: 'Colombo Fort',
    accountNo: 'XXXX-XXXX-XXXX',
    accountName: 'LankaCommerce Cloud (Pvt) Ltd',
  },
  {
    bank: 'Bank of Ceylon',
    branch: 'Colombo',
    accountNo: 'XXXX-XXXX-XXXX',
    accountName: 'LankaCommerce Cloud (Pvt) Ltd',
  },
  {
    bank: 'Sampath Bank',
    branch: 'Colombo',
    accountNo: 'XXXX-XXXX-XXXX',
    accountName: 'LankaCommerce Cloud (Pvt) Ltd',
  },
] as const;

export const installmentPlans = [
  { months: 3, minAmount: 10000, label: '3-Month Installment' },
  { months: 6, minAmount: 10000, label: '6-Month Installment' },
  { months: 12, minAmount: 25000, label: '12-Month Installment' },
] as const;

export const paymentConfig = {
  methods: paymentMethods,
  bankAccounts,
  installmentPlans,
  globalMinAmount: 100,
  globalMaxAmount: 500000,
  currency: 'LKR',
} as const;
