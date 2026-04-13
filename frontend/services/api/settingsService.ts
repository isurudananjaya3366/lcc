/**
 * Settings Service
 *
 * Type-safe operations for tenant settings, category-specific settings,
 * feature flags, logo upload, and tax rate management.
 */

import { apiClient } from './apiClient';
import type { APIResponse } from '@/types/api';

// ── Local Types ────────────────────────────────────────────────

export enum SettingCategory {
  GENERAL = 'general',
  BILLING = 'billing',
  INVENTORY = 'inventory',
  POS = 'pos',
  NOTIFICATIONS = 'notifications',
  LOCALIZATION = 'localization',
  APPEARANCE = 'appearance',
  INTEGRATIONS = 'integrations',
}

export interface Setting {
  key: string;
  value: string | number | boolean | Record<string, unknown>;
  category: SettingCategory;
  label: string;
  description?: string;
  type: 'string' | 'number' | 'boolean' | 'json';
  isEditable: boolean;
}

export interface TenantSettings {
  tenantId: string;
  tenantName: string;
  settings: Setting[];
  updatedAt: string;
}

export interface TaxRate {
  id: string;
  name: string;
  rate: number;
  isDefault: boolean;
  isActive: boolean;
}

export interface FeatureFlag {
  key: string;
  enabled: boolean;
  description?: string;
}

const SETTINGS_ENDPOINT = '/api/v1/settings';

// ── Tenant Settings ────────────────────────────────────────────

async function getTenantSettings(): Promise<APIResponse<TenantSettings>> {
  const { data } = await apiClient.get(`${SETTINGS_ENDPOINT}/`);
  return data;
}

async function updateTenantSettings(
  updates: Record<string, string | number | boolean | Record<string, unknown>>
): Promise<APIResponse<TenantSettings>> {
  const { data } = await apiClient.patch(`${SETTINGS_ENDPOINT}/`, updates);
  return data;
}

async function getCategorySettings(
  category: SettingCategory
): Promise<APIResponse<Setting[]>> {
  const { data } = await apiClient.get(`${SETTINGS_ENDPOINT}/category/${category}/`);
  return data;
}

async function updateCategorySetting(
  category: SettingCategory,
  key: string,
  value: string | number | boolean | Record<string, unknown>
): Promise<APIResponse<Setting>> {
  const { data } = await apiClient.patch(
    `${SETTINGS_ENDPOINT}/category/${category}/`,
    { key, value }
  );
  return data;
}

// ── Feature Flags ──────────────────────────────────────────────

async function getFeatureFlags(): Promise<APIResponse<FeatureFlag[]>> {
  const { data } = await apiClient.get(`${SETTINGS_ENDPOINT}/features/`);
  return data;
}

async function toggleFeatureFlag(
  key: string,
  enabled: boolean
): Promise<APIResponse<FeatureFlag>> {
  const { data } = await apiClient.patch(`${SETTINGS_ENDPOINT}/features/${key}/`, {
    enabled,
  });
  return data;
}

// ── Logo / Branding ────────────────────────────────────────────

async function uploadLogo(file: File): Promise<APIResponse<{ url: string }>> {
  const formData = new FormData();
  formData.append('logo', file);
  const { data } = await apiClient.post(`${SETTINGS_ENDPOINT}/logo/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

async function deleteLogo(): Promise<APIResponse<void>> {
  const { data } = await apiClient.delete(`${SETTINGS_ENDPOINT}/logo/`);
  return data;
}

// ── Tax Rates ──────────────────────────────────────────────────

async function getTaxRates(): Promise<APIResponse<TaxRate[]>> {
  const { data } = await apiClient.get(`${SETTINGS_ENDPOINT}/tax-rates/`);
  return data;
}

async function createTaxRate(
  taxData: Omit<TaxRate, 'id'>
): Promise<APIResponse<TaxRate>> {
  const { data } = await apiClient.post(
    `${SETTINGS_ENDPOINT}/tax-rates/`,
    taxData
  );
  return data;
}

async function updateTaxRate(
  id: string,
  taxData: Partial<TaxRate>
): Promise<APIResponse<TaxRate>> {
  const { data } = await apiClient.patch(
    `${SETTINGS_ENDPOINT}/tax-rates/${id}/`,
    taxData
  );
  return data;
}

async function deleteTaxRate(id: string): Promise<APIResponse<void>> {
  const { data } = await apiClient.delete(`${SETTINGS_ENDPOINT}/tax-rates/${id}/`);
  return data;
}

const settingsService = {
  getTenantSettings,
  updateTenantSettings,
  getCategorySettings,
  updateCategorySetting,
  getFeatureFlags,
  toggleFeatureFlag,
  uploadLogo,
  deleteLogo,
  getTaxRates,
  createTaxRate,
  updateTaxRate,
  deleteTaxRate,
};

export default settingsService;
