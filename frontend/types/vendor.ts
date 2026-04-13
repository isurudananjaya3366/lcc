/**
 * Vendor Types
 *
 * Comprehensive TypeScript types for vendor management including
 * vendor entities, contacts, payment terms, purchase history,
 * and performance tracking.
 */

// ── Enums ──────────────────────────────────────────────────────

export enum VendorType {
  SUPPLIER = 'SUPPLIER',
  MANUFACTURER = 'MANUFACTURER',
  DISTRIBUTOR = 'DISTRIBUTOR',
  SERVICE_PROVIDER = 'SERVICE_PROVIDER',
  CONTRACTOR = 'CONTRACTOR',
}

export enum VendorStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  SUSPENDED = 'SUSPENDED',
  BLOCKED = 'BLOCKED',
  PROSPECT = 'PROSPECT',
}

export enum VendorCategory {
  RAW_MATERIALS = 'RAW_MATERIALS',
  FINISHED_GOODS = 'FINISHED_GOODS',
  SERVICES = 'SERVICES',
  EQUIPMENT = 'EQUIPMENT',
  UTILITIES = 'UTILITIES',
}

export enum VendorPaymentTerms {
  NET_7 = 'NET_7',
  NET_15 = 'NET_15',
  NET_30 = 'NET_30',
  NET_45 = 'NET_45',
  NET_60 = 'NET_60',
  NET_90 = 'NET_90',
  COD = 'COD',
  PREPAID = 'PREPAID',
}

// ── Supporting Interfaces ──────────────────────────────────────

export interface VendorContact {
  id: string;
  vendorId: string;
  firstName: string;
  lastName: string;
  title?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  department?: string;
  isPrimary: boolean;
  isAccounts: boolean;
  isProcurement: boolean;
}

export interface VendorAddress {
  id: string;
  vendorId: string;
  addressType: 'OFFICE' | 'WAREHOUSE' | 'BILLING';
  street: string;
  street2?: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
  isDefault: boolean;
  notes?: string;
}

export interface VendorBankAccount {
  id: string;
  vendorId: string;
  bankName: string;
  accountName: string;
  accountNumber: string;
  routingNumber?: string;
  swiftCode?: string;
  currency: string;
  isDefault: boolean;
}

export interface VendorProduct {
  id: string;
  vendorId: string;
  productId: string;
  vendorSKU?: string;
  unitCost: number;
  moq: number;
  leadTimeDays: number;
  isPreferred: boolean;
  lastPurchaseDate?: string;
  lastPurchasePrice?: number;
}

export interface VendorPerformance {
  id: string;
  vendorId: string;
  period: string;
  totalOrders: number;
  totalValue: number;
  averageOrderValue: number;
  onTimeDeliveryRate: number;
  qualityRating: number;
  responseTime: number;
  defectRate: number;
  returnRate: number;
}

export interface VendorGroup {
  id: string;
  name: string;
  description?: string;
  criteria?: string;
  vendorCount: number;
  isActive: boolean;
}

export interface PurchaseOrder {
  id: string;
  poNumber: string;
  vendorId: string;
  orderDate: string;
  expectedDate?: string;
  status: 'DRAFT' | 'SENT' | 'ACKNOWLEDGED' | 'SHIPPED' | 'RECEIVED' | 'CANCELLED';
  items: {
    productId: string;
    variantId?: string;
    quantity: number;
    unitCost: number;
    total: number;
  }[];
  subtotal: number;
  tax: number;
  shipping: number;
  total: number;
  shippingAddress?: VendorAddress;
  billingAddress?: VendorAddress;
  notes?: string;
  terms?: string;
  createdBy: string;
  createdAt: string;
}

export interface VendorInvoice {
  id: string;
  invoiceNumber: string;
  vendorId: string;
  purchaseOrderId?: string;
  invoiceDate: string;
  dueDate: string;
  status: 'PENDING' | 'APPROVED' | 'PAID' | 'OVERDUE' | 'CANCELLED';
  items: {
    description: string;
    quantity: number;
    unitCost: number;
    total: number;
  }[];
  subtotal: number;
  tax: number;
  total: number;
  amountPaid: number;
  amountDue: number;
  paymentDate?: string;
  notes?: string;
}

export interface VendorPayment {
  id: string;
  vendorId: string;
  paymentNumber: string;
  paymentDate: string;
  amount: number;
  paymentMethod: string;
  referenceNumber?: string;
  invoices: { invoiceId: string; amount: number }[];
  notes?: string;
  createdBy: string;
}

// ── Main Entity ────────────────────────────────────────────────

export interface Vendor {
  id: string;
  tenantId: string;
  vendorNumber: string;
  vendorType: VendorType;
  status: VendorStatus;
  companyName: string;
  tradeName?: string;
  legalName?: string;
  taxId?: string;
  email?: string;
  phone?: string;
  fax?: string;
  website?: string;
  category: VendorCategory;
  paymentTerms: VendorPaymentTerms;
  currency: string;
  addresses?: VendorAddress[];
  contacts?: VendorContact[];
  bankAccounts?: VendorBankAccount[];
  creditRating?: string;
  totalPurchases: number;
  averageLeadTime?: number;
  tags?: string[];
  customFields?: Record<string, unknown>;
  notes?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

// ── API Request/Response Interfaces ────────────────────────────

export interface VendorCreateRequest {
  companyName: string;
  tradeName?: string;
  legalName?: string;
  vendorType: VendorType;
  category: VendorCategory;
  taxId?: string;
  email?: string;
  phone?: string;
  fax?: string;
  website?: string;
  paymentTerms?: VendorPaymentTerms;
  currency?: string;
  addresses?: Omit<VendorAddress, 'id' | 'vendorId'>[];
  contacts?: Omit<VendorContact, 'id' | 'vendorId'>[];
  bankAccounts?: Omit<VendorBankAccount, 'id' | 'vendorId'>[];
  tags?: string[];
  customFields?: Record<string, unknown>;
}

export interface VendorUpdateRequest {
  companyName?: string;
  tradeName?: string;
  legalName?: string;
  vendorType?: VendorType;
  status?: VendorStatus;
  category?: VendorCategory;
  taxId?: string;
  email?: string;
  phone?: string;
  fax?: string;
  website?: string;
  paymentTerms?: VendorPaymentTerms;
  currency?: string;
  tags?: string[];
  customFields?: Record<string, unknown>;
}

export interface VendorSearchParams {
  query?: string;
  vendorType?: VendorType;
  status?: VendorStatus;
  category?: VendorCategory;
  tags?: string[];
  performanceRating?: number;
  sort?: string;
  page?: number;
  pageSize?: number;
}
