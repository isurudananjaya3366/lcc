/**
 * Customer Types
 *
 * Comprehensive TypeScript types for customer management including
 * customer entities, addresses, contacts, payment methods,
 * transaction history, and loyalty programs.
 */

// ── Enums ──────────────────────────────────────────────────────

export enum CustomerType {
  INDIVIDUAL = 'INDIVIDUAL',
  BUSINESS = 'BUSINESS',
  WHOLESALER = 'WHOLESALER',
  DISTRIBUTOR = 'DISTRIBUTOR',
}

export enum CustomerStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  SUSPENDED = 'SUSPENDED',
  BLOCKED = 'BLOCKED',
}

export enum PaymentTerms {
  NET_0 = 'NET_0',
  NET_15 = 'NET_15',
  NET_30 = 'NET_30',
  NET_45 = 'NET_45',
  NET_60 = 'NET_60',
  COD = 'COD',
  PREPAID = 'PREPAID',
}

// ── Supporting Interfaces ──────────────────────────────────────

export interface CustomerAddress {
  id: string;
  customerId: string;
  addressType: 'BILLING' | 'SHIPPING' | 'BOTH';
  street: string;
  street2?: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
  isDefault: boolean;
  label?: string;
  notes?: string;
}

export interface CustomerContact {
  id: string;
  customerId: string;
  firstName: string;
  lastName: string;
  title?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  isPrimary: boolean;
}

export interface CustomerPaymentMethod {
  id: string;
  customerId: string;
  type: 'CASH' | 'CARD' | 'BANK_TRANSFER';
  cardLastFour?: string;
  cardBrand?: string;
  expiryMonth?: number;
  expiryYear?: number;
  bankName?: string;
  accountLastFour?: string;
  isDefault: boolean;
}

export interface CustomerCreditLimit {
  creditLimit: number;
  currentBalance: number;
  availableCredit: number;
  paymentTerms: PaymentTerms;
  overdueDays: number;
  lastPaymentDate?: string;
}

export interface CustomerLoyalty {
  id: string;
  customerId: string;
  tierLevel: string;
  points: number;
  lifetimeValue: number;
  memberSince: string;
  lastPurchaseDate?: string;
  purchaseCount: number;
  rewardsEarned: number;
  rewardsRedeemed: number;
}

export interface CustomerNote {
  id: string;
  customerId: string;
  note: string;
  category?: string;
  createdBy: string;
  createdAt: string;
  isPrivate: boolean;
}

export interface CustomerGroup {
  id: string;
  name: string;
  description?: string;
  criteria?: string;
  discountPercentage?: number;
  priceTierId?: string;
  customerCount: number;
  isActive: boolean;
}

export interface CustomerTransaction {
  id: string;
  customerId: string;
  transactionType: 'SALE' | 'PAYMENT' | 'REFUND' | 'CREDIT';
  amount: number;
  balance: number;
  referenceType?: string;
  referenceId?: string;
  transactionDate: string;
  notes?: string;
}

// ── Main Entity ────────────────────────────────────────────────

export interface Customer {
  id: string;
  tenantId: string;
  customerNumber: string;
  customerType: CustomerType;
  status: CustomerStatus;
  firstName?: string;
  lastName?: string;
  companyName?: string;
  displayName: string;
  email?: string;
  phone?: string;
  mobile?: string;
  taxId?: string;
  addresses?: CustomerAddress[];
  contacts?: CustomerContact[];
  paymentMethods?: CustomerPaymentMethod[];
  creditLimit?: CustomerCreditLimit;
  loyalty?: CustomerLoyalty;
  priceTierId?: string;
  tags?: string[];
  customFields?: Record<string, unknown>;
  preferences?: Record<string, unknown>;
  totalOrders: number;
  totalSpent: number;
  averageOrderValue: number;
  lastOrderDate?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

// ── API Request/Response Interfaces ────────────────────────────

export interface CustomerCreateRequest {
  customerType: CustomerType;
  firstName?: string;
  lastName?: string;
  companyName?: string;
  displayName?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  taxId?: string;
  addresses?: Omit<CustomerAddress, 'id' | 'customerId'>[];
  contacts?: Omit<CustomerContact, 'id' | 'customerId'>[];
  creditLimit?: Partial<CustomerCreditLimit>;
  tags?: string[];
  customFields?: Record<string, unknown>;
}

export interface CustomerUpdateRequest {
  customerType?: CustomerType;
  status?: CustomerStatus;
  firstName?: string;
  lastName?: string;
  companyName?: string;
  displayName?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  taxId?: string;
  priceTierId?: string;
  tags?: string[];
  customFields?: Record<string, unknown>;
  preferences?: Record<string, unknown>;
}

export interface CustomerSearchParams {
  query?: string;
  customerType?: CustomerType;
  status?: CustomerStatus;
  groupId?: string;
  creditStatus?: 'GOOD' | 'OVERDUE' | 'EXCEEDED';
  tags?: string[];
  orderDateFrom?: string;
  orderDateTo?: string;
  sort?: string;
  page?: number;
  pageSize?: number;
}

export interface CustomerStatement {
  customerId: string;
  periodStart: string;
  periodEnd: string;
  openingBalance: number;
  closingBalance: number;
  transactions: CustomerTransaction[];
  totalSales: number;
  totalPayments: number;
  outstandingAmount: number;
  overdueAmount: number;
}
