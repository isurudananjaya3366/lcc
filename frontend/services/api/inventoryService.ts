/**
 * Inventory Service
 *
 * Type-safe operations for stock management, warehouse operations,
 * stock movements, transfers, and adjustments.
 */

import { apiClient } from './apiClient';
import type { APIResponse, PaginatedResponse } from '@/types/api';
import type {
  StockLevel,
  StockMovement,
  StockMovementType,
  StockMovementStatus,
  StockMovementCreateRequest,
  StockAdjustment,
  StockAdjustmentCreateRequest,
  StockTransfer,
  StockTransferCreateRequest,
  StockCount,
  LowStockAlert,
  InventoryValue,
  InventorySearchParams,
} from '@/types/inventory';

const INVENTORY_ENDPOINT = '/api/v1/inventory';

// ── Stock Levels ───────────────────────────────────────────────

async function getStockLevels(
  params?: InventorySearchParams
): Promise<PaginatedResponse<StockLevel>> {
  const { data } = await apiClient.get(`${INVENTORY_ENDPOINT}/stock-levels/`, { params });
  return data;
}

async function getStockLevelByProduct(
  productId: string,
  warehouseId?: string
): Promise<APIResponse<StockLevel[]>> {
  const { data } = await apiClient.get(
    `${INVENTORY_ENDPOINT}/stock-levels/product/${productId}/`,
    { params: warehouseId ? { warehouseId } : undefined }
  );
  return data;
}

async function getStockLevelByWarehouse(
  warehouseId: string,
  categoryId?: string
): Promise<PaginatedResponse<StockLevel>> {
  const { data } = await apiClient.get(
    `${INVENTORY_ENDPOINT}/stock-levels/warehouse/${warehouseId}/`,
    { params: categoryId ? { categoryId } : undefined }
  );
  return data;
}

// ── Stock Movements ────────────────────────────────────────────

async function getStockMovements(params?: {
  productId?: string;
  warehouseId?: string;
  movementType?: StockMovementType;
  startDate?: string;
  endDate?: string;
}): Promise<PaginatedResponse<StockMovement>> {
  const { data } = await apiClient.get(`${INVENTORY_ENDPOINT}/movements/`, { params });
  return data;
}

async function createStockMovement(
  movementData: StockMovementCreateRequest
): Promise<APIResponse<StockMovement>> {
  const { data } = await apiClient.post(`${INVENTORY_ENDPOINT}/movements/`, movementData);
  return data;
}

// ── Stock Adjustments ──────────────────────────────────────────

async function getStockAdjustments(params?: {
  warehouseId?: string;
  startDate?: string;
  endDate?: string;
}): Promise<PaginatedResponse<StockAdjustment>> {
  const { data } = await apiClient.get(`${INVENTORY_ENDPOINT}/adjustments/`, { params });
  return data;
}

async function createStockAdjustment(
  adjustmentData: StockAdjustmentCreateRequest
): Promise<APIResponse<StockAdjustment>> {
  const { data } = await apiClient.post(`${INVENTORY_ENDPOINT}/adjustments/`, adjustmentData);
  return data;
}

// ── Stock Transfers ────────────────────────────────────────────

async function getStockTransfers(params?: {
  sourceWarehouseId?: string;
  destinationWarehouseId?: string;
  status?: StockMovementStatus;
}): Promise<PaginatedResponse<StockTransfer>> {
  const { data } = await apiClient.get(`${INVENTORY_ENDPOINT}/transfers/`, { params });
  return data;
}

async function getStockTransferById(
  id: string
): Promise<APIResponse<StockTransfer>> {
  const { data } = await apiClient.get(`${INVENTORY_ENDPOINT}/transfers/${id}/`);
  return data;
}

async function createStockTransfer(
  transferData: StockTransferCreateRequest
): Promise<APIResponse<StockTransfer>> {
  const { data } = await apiClient.post(`${INVENTORY_ENDPOINT}/transfers/`, transferData);
  return data;
}

async function approveStockTransfer(
  id: string,
  notes?: string
): Promise<APIResponse<StockTransfer>> {
  const { data } = await apiClient.post(
    `${INVENTORY_ENDPOINT}/transfers/${id}/approve/`,
    notes ? { notes } : undefined
  );
  return data;
}

async function completeStockTransfer(
  id: string,
  receivedItems: { productId: string; variantId?: string; quantityReceived: number }[]
): Promise<APIResponse<StockTransfer>> {
  const { data } = await apiClient.post(
    `${INVENTORY_ENDPOINT}/transfers/${id}/complete/`,
    { receivedItems }
  );
  return data;
}

async function cancelStockTransfer(
  id: string,
  reason: string
): Promise<APIResponse<StockTransfer>> {
  const { data } = await apiClient.post(
    `${INVENTORY_ENDPOINT}/transfers/${id}/cancel/`,
    { reason }
  );
  return data;
}

// ── Stock Counts ───────────────────────────────────────────────

async function performStockCount(countData: {
  warehouseId: string;
  countType: string;
  items: { productId: string; variantId?: string; countedQuantity: number }[];
}): Promise<APIResponse<StockCount>> {
  const { data } = await apiClient.post(`${INVENTORY_ENDPOINT}/stock-counts/`, countData);
  return data;
}

async function getStockCountById(
  id: string
): Promise<APIResponse<StockCount>> {
  const { data } = await apiClient.get(`${INVENTORY_ENDPOINT}/stock-counts/${id}/`);
  return data;
}

// ── Alerts ─────────────────────────────────────────────────────

async function getLowStockAlerts(
  warehouseId?: string
): Promise<APIResponse<LowStockAlert[]>> {
  const { data } = await apiClient.get(`${INVENTORY_ENDPOINT}/low-stock-alerts/`, {
    params: warehouseId ? { warehouseId } : undefined,
  });
  return data;
}

async function acknowledgeAlert(alertId: string): Promise<APIResponse<void>> {
  const { data } = await apiClient.post(
    `${INVENTORY_ENDPOINT}/low-stock-alerts/${alertId}/acknowledge/`
  );
  return data;
}

// ── Valuation ──────────────────────────────────────────────────

async function getInventoryValue(
  warehouseId?: string,
  date?: string
): Promise<APIResponse<InventoryValue>> {
  const { data } = await apiClient.get(`${INVENTORY_ENDPOINT}/valuation/`, {
    params: { warehouseId, date },
  });
  return data;
}

// ── Reservation ────────────────────────────────────────────────

async function reserveStock(
  productId: string,
  variantId: string | undefined,
  quantity: number,
  warehouseId: string,
  referenceType: string,
  referenceId: string
): Promise<APIResponse<void>> {
  const { data } = await apiClient.post(`${INVENTORY_ENDPOINT}/reserve/`, {
    productId,
    variantId,
    quantity,
    warehouseId,
    referenceType,
    referenceId,
  });
  return data;
}

async function releaseStock(
  referenceType: string,
  referenceId: string
): Promise<APIResponse<void>> {
  const { data } = await apiClient.post(`${INVENTORY_ENDPOINT}/release/`, {
    referenceType,
    referenceId,
  });
  return data;
}

const inventoryService = {
  getStockLevels,
  getStockLevelByProduct,
  getStockLevelByWarehouse,
  getStockMovements,
  createStockMovement,
  getStockAdjustments,
  createStockAdjustment,
  getStockTransfers,
  getStockTransferById,
  createStockTransfer,
  approveStockTransfer,
  completeStockTransfer,
  cancelStockTransfer,
  performStockCount,
  getStockCountById,
  getLowStockAlerts,
  acknowledgeAlert,
  getInventoryValue,
  reserveStock,
  releaseStock,
};

export default inventoryService;
