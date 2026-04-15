// ================================================================
// POS Module Types — Task 13
// ================================================================
// Comprehensive TypeScript types for the POS interface module
// ================================================================

// ── Cart Types ─────────────────────────────────────────────────

export interface POSCartItem {
  id: string;
  productId: string;
  productName: string;
  sku: string;
  variantId?: string;
  variantName?: string;
  quantity: number;
  unitPrice: number;
  originalPrice: number;
  discount?: POSDiscount;
  discountAmount: number;
  taxRate: number;
  taxAmount: number;
  lineTotal: number;
  imageUrl?: string;
  isTaxable: boolean;
  addedAt: string;
}

// ── Shift Types ────────────────────────────────────────────────

export type ShiftStatus = 'open' | 'paused' | 'closed';

export interface POSShift {
  id: string;
  sessionNumber: string;
  terminalId: string;
  terminalName: string;
  cashierId: string;
  cashierName: string;
  status: ShiftStatus;
  openedAt: string;
  closedAt?: string;
  openingCash: number;
  expectedCash: number;
  actualCash?: number;
  transactionCount: number;
  totalSales: number;
  totalRefunds: number;
  netSales: number;
  variance?: number;
}

// ── Customer Types ─────────────────────────────────────────────

export interface POSCustomer {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  loyaltyPoints?: number;
  customerType: 'regular' | 'loyalty' | 'vip';
  discountEligibility?: number;
}

// ── Payment Types ──────────────────────────────────────────────

export type PaymentMethod = 'cash' | 'card' | 'bank_transfer' | 'mobile' | 'store_credit';

export type PaymentStatus = 'pending' | 'completed' | 'failed' | 'refunded' | 'voided';

export interface POSPayment {
  id: string;
  method: PaymentMethod;
  amount: number;
  status: PaymentStatus;
  reference?: string;
  authorizationCode?: string;
  amountTendered?: number;
  changeDue?: number;
  paidAt?: string;
}

// ── Discount Types ─────────────────────────────────────────────

export type DiscountType = 'percentage' | 'fixed';

export interface POSDiscount {
  type: DiscountType;
  value: number;
  reason?: string;
  couponCode?: string;
  appliedBy?: string;
  appliedAt?: string;
}

// ── Sale Types ─────────────────────────────────────────────────

export type SaleStatus = 'active' | 'held' | 'completed' | 'voided' | 'abandoned';

export interface POSSale {
  id: string;
  referenceNumber: string;
  items: POSCartItem[];
  customer?: POSCustomer;
  discount?: POSDiscount;
  payments: POSPayment[];
  subtotal: number;
  discountAmount: number;
  taxAmount: number;
  grandTotal: number;
  status: SaleStatus;
  heldReason?: string;
  createdAt: string;
  completedAt?: string;
}

// ── Modal Types ────────────────────────────────────────────────

export type POSModalType =
  | 'payment'
  | 'discount'
  | 'customer'
  | 'receipt'
  | 'shift_open'
  | 'shift_close'
  | 'variant_select'
  | 'hold_sale'
  | 'retrieve_hold'
  | 'exit_confirm'
  | 'clear_cart'
  | 'keyboard_shortcuts'
  | null;

// ── Quick Button Types ─────────────────────────────────────────

export interface QuickButtonGroup {
  id: string;
  name: string;
  icon?: string;
  color?: string;
  displayOrder: number;
  rows: number;
  columns: number;
  buttons: QuickButton[];
}

export interface QuickButton {
  id: string;
  productId: string;
  label: string;
  imageUrl?: string;
  color?: string;
  price: number;
  inStock: boolean;
  stockQuantity: number;
  quickQuantity: number;
  hasVariants?: boolean;
  row: number;
  column: number;
}

// ── Search Types ───────────────────────────────────────────────

export interface ProductSearchResult {
  id: string;
  name: string;
  sku: string;
  barcode?: string;
  price: number;
  stockQuantity: number;
  imageUrl?: string;
  categoryName?: string;
  hasVariants: boolean;
  variants?: ProductVariant[];
}

export interface ProductVariant {
  id: string;
  name: string;
  sku: string;
  price: number;
  stockQuantity: number;
  attributes: Record<string, string>;
}

// ── Receipt Types ──────────────────────────────────────────────

export interface POSReceipt {
  id: string;
  receiptNumber: string;
  type: 'sale' | 'refund' | 'void' | 'duplicate';
  sale: POSSale;
  generatedAt: string;
  printedAt?: string;
  emailedAt?: string;
}

// ── Context State Types ────────────────────────────────────────

export interface POSState {
  cartItems: POSCartItem[];
  currentShift: POSShift | null;
  customer: POSCustomer | null;
  cartDiscount: POSDiscount | null;
  activeModal: POSModalType;
  isLoading: boolean;
  heldSales: POSSale[];
}

export interface POSActions {
  // Cart actions
  addToCart: (
    item: Omit<POSCartItem, 'id' | 'addedAt' | 'lineTotal' | 'discountAmount' | 'taxAmount'>
  ) => void;
  updateQuantity: (itemId: string, quantity: number) => void;
  removeFromCart: (itemId: string) => void;
  clearCart: () => void;
  applyItemDiscount: (itemId: string, discount: POSDiscount) => void;
  removeItemDiscount: (itemId: string) => void;

  // Cart-level discount
  applyCartDiscount: (discount: POSDiscount) => void;
  removeCartDiscount: () => void;

  // Customer
  setCustomer: (customer: POSCustomer | null) => void;

  // Shift
  setShift: (shift: POSShift | null) => void;

  // Modal
  openModal: (modal: POSModalType) => void;
  closeModal: () => void;

  // Hold/Retrieve
  holdSale: (reason?: string) => void;
  retrieveHeldSale: (saleId: string) => void;

  // Computed
  getSubtotal: () => number;
  getDiscountTotal: () => number;
  getTaxTotal: () => number;
  getGrandTotal: () => number;
  getItemCount: () => number;
}

export type POSContextType = POSState & POSActions;
