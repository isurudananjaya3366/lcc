/**
 * Warehouse Service
 *
 * CRUD operations for warehouse locations, configurations,
 * and operational settings.
 */

import { apiClient } from './apiClient';
import type { APIResponse } from '@/types/api';
import type { Warehouse, WarehouseLocation } from '@/types/inventory';

const WAREHOUSE_ENDPOINT = '/api/v1/warehouses';

// ── Warehouse-specific types ───────────────────────────────────

export interface WarehouseCreateRequest {
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
  capacity?: number;
  isPrimary?: boolean;
  isActive?: boolean;
}

export type WarehouseUpdateRequest = Partial<WarehouseCreateRequest>;

export interface LocationCreateRequest {
  warehouseId: string;
  zone?: string;
  aisle?: string;
  rack?: string;
  shelf?: string;
  bin?: string;
  capacity?: number;
  isActive?: boolean;
}

// ── Warehouse CRUD ─────────────────────────────────────────────

async function getWarehouses(
  includeInactive?: boolean
): Promise<APIResponse<Warehouse[]>> {
  const { data } = await apiClient.get(`${WAREHOUSE_ENDPOINT}/`, {
    params: includeInactive ? { includeInactive: true } : undefined,
  });
  return data;
}

async function getWarehouseById(id: string): Promise<APIResponse<Warehouse>> {
  const { data } = await apiClient.get(`${WAREHOUSE_ENDPOINT}/${id}/`);
  return data;
}

async function getWarehouseByCode(code: string): Promise<APIResponse<Warehouse>> {
  const { data } = await apiClient.get(`${WAREHOUSE_ENDPOINT}/by-code/${code}/`);
  return data;
}

async function createWarehouse(
  warehouseData: WarehouseCreateRequest
): Promise<APIResponse<Warehouse>> {
  const { data } = await apiClient.post(`${WAREHOUSE_ENDPOINT}/`, warehouseData);
  return data;
}

async function updateWarehouse(
  id: string,
  warehouseData: WarehouseUpdateRequest
): Promise<APIResponse<Warehouse>> {
  const { data } = await apiClient.patch(`${WAREHOUSE_ENDPOINT}/${id}/`, warehouseData);
  return data;
}

async function deleteWarehouse(id: string): Promise<APIResponse<void>> {
  const { data } = await apiClient.delete(`${WAREHOUSE_ENDPOINT}/${id}/`);
  return data;
}

async function setPrimaryWarehouse(id: string): Promise<APIResponse<Warehouse>> {
  const { data } = await apiClient.post(`${WAREHOUSE_ENDPOINT}/${id}/set-primary/`);
  return data;
}

// ── Location Management ────────────────────────────────────────

async function getWarehouseLocations(
  warehouseId: string
): Promise<APIResponse<WarehouseLocation[]>> {
  const { data } = await apiClient.get(`${WAREHOUSE_ENDPOINT}/${warehouseId}/locations/`);
  return data;
}

async function createWarehouseLocation(
  locationData: LocationCreateRequest
): Promise<APIResponse<WarehouseLocation>> {
  const { data } = await apiClient.post(`${WAREHOUSE_ENDPOINT}/locations/`, locationData);
  return data;
}

async function updateWarehouseLocation(
  id: string,
  locationData: Partial<LocationCreateRequest>
): Promise<APIResponse<WarehouseLocation>> {
  const { data } = await apiClient.patch(`${WAREHOUSE_ENDPOINT}/locations/${id}/`, locationData);
  return data;
}

async function deleteWarehouseLocation(id: string): Promise<APIResponse<void>> {
  const { data } = await apiClient.delete(`${WAREHOUSE_ENDPOINT}/locations/${id}/`);
  return data;
}

// ── Utilization ────────────────────────────────────────────────

async function getWarehouseUtilization(
  id: string
): Promise<APIResponse<{ capacity: number; utilized: number; percentage: number }>> {
  const { data } = await apiClient.get(`${WAREHOUSE_ENDPOINT}/${id}/utilization/`);
  return data;
}

const warehouseService = {
  getWarehouses,
  getWarehouseById,
  getWarehouseByCode,
  createWarehouse,
  updateWarehouse,
  deleteWarehouse,
  setPrimaryWarehouse,
  getWarehouseLocations,
  createWarehouseLocation,
  updateWarehouseLocation,
  deleteWarehouseLocation,
  getWarehouseUtilization,
};

export default warehouseService;
