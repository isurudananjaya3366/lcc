/**
 * Category Service
 *
 * CRUD operations for product categories with hierarchical structure support.
 */

import { apiClient } from './apiClient';
import type { APIResponse, PaginatedResponse } from '@/types/api';
import type { ProductCategory } from '@/types/product';

const CATEGORY_ENDPOINT = '/api/v1/categories';

// ── Category-specific types ────────────────────────────────────

export interface CategoryCreateRequest {
  name: string;
  slug?: string;
  description?: string;
  parentId?: string;
  imageUrl?: string;
  displayOrder?: number;
  isActive?: boolean;
  seoMetadata?: { title?: string; description?: string; keywords?: string[] };
}

export type CategoryUpdateRequest = Partial<CategoryCreateRequest>;

export interface CategoryTreeNode extends ProductCategory {
  children: CategoryTreeNode[];
  level: number;
  path: string[];
}

// ── Service Functions ──────────────────────────────────────────

async function getCategories(
  params?: { parentId?: string; includeInactive?: boolean }
): Promise<PaginatedResponse<ProductCategory>> {
  const { data } = await apiClient.get(`${CATEGORY_ENDPOINT}/`, { params });
  return data;
}

async function getCategoryTree(): Promise<APIResponse<CategoryTreeNode[]>> {
  const { data } = await apiClient.get(`${CATEGORY_ENDPOINT}/tree/`);
  return data;
}

async function getCategoryById(
  id: string
): Promise<APIResponse<ProductCategory>> {
  const { data } = await apiClient.get(`${CATEGORY_ENDPOINT}/${id}/`);
  return data;
}

async function getCategoryBySlug(
  slug: string
): Promise<APIResponse<ProductCategory>> {
  const { data } = await apiClient.get(`${CATEGORY_ENDPOINT}/by-slug/${slug}/`);
  return data;
}

async function createCategory(
  categoryData: CategoryCreateRequest
): Promise<APIResponse<ProductCategory>> {
  const { data } = await apiClient.post(`${CATEGORY_ENDPOINT}/`, categoryData);
  return data;
}

async function updateCategory(
  id: string,
  categoryData: CategoryUpdateRequest
): Promise<APIResponse<ProductCategory>> {
  const { data } = await apiClient.patch(
    `${CATEGORY_ENDPOINT}/${id}/`,
    categoryData
  );
  return data;
}

async function deleteCategory(
  id: string,
  reassignTo?: string
): Promise<APIResponse<void>> {
  const { data } = await apiClient.delete(`${CATEGORY_ENDPOINT}/${id}/`, {
    params: reassignTo ? { reassignTo } : undefined,
  });
  return data;
}

async function moveCategory(
  id: string,
  newParentId: string | null,
  position?: number
): Promise<APIResponse<ProductCategory>> {
  const { data } = await apiClient.post(`${CATEGORY_ENDPOINT}/move/`, {
    categoryId: id,
    newParentId,
    position,
  });
  return data;
}

async function reorderCategories(
  parentId: string | null,
  categoryOrder: string[]
): Promise<APIResponse<void>> {
  const { data } = await apiClient.put(`${CATEGORY_ENDPOINT}/reorder/`, {
    parentId,
    categoryOrder,
  });
  return data;
}

async function getCategoryPath(
  id: string
): Promise<APIResponse<ProductCategory[]>> {
  const { data } = await apiClient.get(`${CATEGORY_ENDPOINT}/${id}/path/`);
  return data;
}

const categoryService = {
  getCategories,
  getCategoryTree,
  getCategoryById,
  getCategoryBySlug,
  createCategory,
  updateCategory,
  deleteCategory,
  moveCategory,
  reorderCategories,
  getCategoryPath,
};

export default categoryService;
