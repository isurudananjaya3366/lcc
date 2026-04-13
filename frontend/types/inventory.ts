/**
 * Inventory Types
 *
 * Comprehensive TypeScript types for inventory management including
 * stock tracking, warehouse locations, movements, and adjustments.
 */

// ── Enums ──────────────────────────────────────────────────────

export enum StockMovementType {
  PURCHASE = 'PURCHASE',
  SALE = 'SALE',
  ADJUSTMENT = 'ADJUSTMENT',
  TRANSFER = 'TRANSFER',
  RETURN = 'RETURN',
  DAMAGE = 'DAMAGE',
}

export enum StockMovementStatus {
  PENDING = 'PENDING',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED',
}

export enum AdjustmentReason {
  DAMAGE = 'DAMAGE',
  THEFT = 'THEFT',
  EXPIRED = 'EXPIRED',
  RECOUNT = 'RECOUNT',
  ERROR = 'ERROR',
  OTHER = 'OTHER',
}

export enum InventoryValuationMethod {
  FIFO = 'FIFO',
  LIFO = 'LIFO',
  AVERAGE = 'AVERAGE',
  STANDARD = 'STANDARD',
}

// ── Location Entities ──────────────────────────────────────────

export interface Warehouse {
  id: string;
  tenantId: string;
  code: string;
  name: string;
  description?: string;
  address: {
    street: string;
    street2?: string;
    city: string;
    state: string;
    postalCode: string;
    country: string;
  };
  contactPhone?: string;
  contactEmail?: string;
  isActive: boolean;
  isPrimary: boolean;
  capacity?: number;
  currentUtilization?: number;
  createdAt: string;
  updatedAt: string;
}

export interface WarehouseLocation {
  id: string;
  warehouseId: string;
  zone?: string;
  aisle?: string;
  rack?: string;
  shelf?: string;
  bin?: string;
  locationCode: string;
  capacity?: number;
  isActive: boolean;
}

// ── Stock Entities ─────────────────────────────────────────────

export interface StockLevel {
  id: string;
  productId: string;
  variantId?: string;
  warehouseId: string;
  quantityOnHand: number;
  quantityAvailable: number;
  quantityReserved: number;
  quantityIncoming: number;
  quantityOnOrder: number;
  lastCountDate?: string;
  lastRestockDate?: string;
}

export interface StockMovement {
  id: string;
  tenantId: string;
  movementType: StockMovementType;
  status: StockMovementStatus;
  productId: string;
  variantId?: string;
  sku: string;
  quantity: number;
  sourceWarehouseId?: string;
  destinationWarehouseId?: string;
  unitCost?: number;
  totalCost?: number;
  referenceType?: string;
  referenceId?: string;
  notes?: string;
  createdBy: string;
  createdAt: string;
  completedAt?: string;
}

export interface StockAdjustment {
  id: string;
  productId: string;
  variantId?: string;
  warehouseId: string;
  quantityBefore: number;
  quantityAfter: number;
  difference: number;
  reason: AdjustmentReason;
  reasonNotes?: string;
  adjustedBy: string;
  adjustedAt: string;
  approvedBy?: string;
  approvalDate?: string;
}

export interface StockTransfer {
  id: string;
  transferNumber: string;
  sourceWarehouseId: string;
  destinationWarehouseId: string;
  items: {
    productId: string;
    variantId?: string;
    quantity: number;
    quantityReceived?: number;
  }[];
  status: StockMovementStatus;
  requestedBy: string;
  approvedBy?: string;
  completedBy?: string;
  requestDate: string;
  approvalDate?: string;
  shipDate?: string;
  receiveDate?: string;
  notes?: string;
  shippingDetails?: string;
}

export interface StockCount {
  id: string;
  countNumber: string;
  warehouseId: string;
  countDate: string;
  countType: 'FULL' | 'CYCLE' | 'SPOT';
  status: StockMovementStatus;
  items: {
    productId: string;
    variantId?: string;
    expectedQuantity: number;
    actualQuantity: number;
    variance: number;
  }[];
  discrepancies: number;
  totalVariance: number;
  countedBy: string;
  approvedBy?: string;
  approvalDate?: string;
}

export interface LowStockAlert {
  id: string;
  productId: string;
  variantId?: string;
  warehouseId: string;
  currentQuantity: number;
  threshold: number;
  status: 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED';
  alertDate: string;
  acknowledgedBy?: string;
  acknowledgedAt?: string;
  reorderQuantity?: number;
  reorderStatus?: string;
}

export interface InventoryValue {
  id: string;
  warehouseId?: string;
  valuationDate: string;
  method: InventoryValuationMethod;
  totalUnits: number;
  totalValue: number;
  averageCost: number;
  categoryBreakdown?: Record<string, { units: number; value: number }>;
  productBreakdown?: Record<string, { units: number; value: number }>;
}

// ── API Request Interfaces ─────────────────────────────────────

export interface StockMovementCreateRequest {
  movementType: StockMovementType;
  productId: string;
  variantId?: string;
  quantity: number;
  sourceWarehouseId?: string;
  destinationWarehouseId?: string;
  unitCost?: number;
  referenceType?: string;
  referenceId?: string;
  notes?: string;
}

export interface StockAdjustmentCreateRequest {
  productId: string;
  variantId?: string;
  warehouseId: string;
  quantityChange: number;
  reason: AdjustmentReason;
  reasonNotes?: string;
}

export interface StockTransferCreateRequest {
  sourceWarehouseId: string;
  destinationWarehouseId: string;
  items: { productId: string; variantId?: string; quantity: number }[];
  requestedDate?: string;
  notes?: string;
}

export interface InventorySearchParams {
  warehouseId?: string;
  productId?: string;
  categoryId?: string;
  lowStock?: boolean;
  outOfStock?: boolean;
  includeInactive?: boolean;
  sort?: string;
  page?: number;
  pageSize?: number;
}
