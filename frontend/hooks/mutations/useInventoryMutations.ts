/**
 * Inventory Mutation Hooks
 *
 * Create / Update / Delete mutations for inventory operations
 * including adjustments, transfers, and warehouses.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import inventoryService from '@/services/api/inventoryService';
import warehouseService from '@/services/api/warehouseService';
import { inventoryKeys } from '@/lib/queryKeys';
import type { StockAdjustmentCreateRequest, StockTransferCreateRequest } from '@/types/inventory';
import type {
  WarehouseCreateRequest,
  WarehouseUpdateRequest,
} from '@/services/api/warehouseService';

// ── Stock Adjustments ──────────────────────────────────────────

export function useCreateStockAdjustment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: StockAdjustmentCreateRequest) =>
      inventoryService.createStockAdjustment(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.all() });
    },
    retry: false,
  });
}

// ── Stock Transfers ────────────────────────────────────────────

export function useCreateStockTransfer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: StockTransferCreateRequest) => inventoryService.createStockTransfer(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.all() });
    },
    retry: false,
  });
}

export function useApproveStockTransfer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, notes }: { id: string; notes?: string }) =>
      inventoryService.approveStockTransfer(id, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.all() });
    },
    retry: false,
  });
}

export function useCompleteStockTransfer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      receivedItems,
    }: {
      id: string;
      receivedItems: { productId: string; variantId?: string; quantityReceived: number }[];
    }) => inventoryService.completeStockTransfer(id, receivedItems),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.all() });
    },
    retry: false,
  });
}

export function useCancelStockTransfer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      inventoryService.cancelStockTransfer(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.all() });
    },
    retry: false,
  });
}

// ── Warehouses ─────────────────────────────────────────────────

export function useCreateWarehouse() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: WarehouseCreateRequest) => warehouseService.createWarehouse(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.all() });
    },
    retry: false,
  });
}

export function useUpdateWarehouse() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: WarehouseUpdateRequest }) =>
      warehouseService.updateWarehouse(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.all() });
    },
    retry: false,
  });
}

export function useDeleteWarehouse() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => warehouseService.deleteWarehouse(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.all() });
    },
    retry: false,
  });
}
