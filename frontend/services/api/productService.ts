/**
 * Product Service
 *
 * Type-safe CRUD operations for products including variant management,
 * image handling, bulk operations, and availability checks.
 */

import { apiClient } from './apiClient';
import type { APIResponse, PaginatedResponse } from '@/types/api';
import type {
  Product,
  ProductCreateRequest,
  ProductUpdateRequest,
  ProductSearchParams,
  ProductBulkOperation,
  ProductVariant,
  ProductImage,
} from '@/types/product';

const PRODUCTS_ENDPOINT = '/api/v1/products';

async function getProducts(
  params?: ProductSearchParams
): Promise<PaginatedResponse<Product>> {
  const { data } = await apiClient.get(`${PRODUCTS_ENDPOINT}/`, { params });
  return data;
}

async function getProductById(id: string): Promise<APIResponse<Product>> {
  const { data } = await apiClient.get(`${PRODUCTS_ENDPOINT}/${id}/`);
  return data;
}

async function getProductBySku(sku: string): Promise<APIResponse<Product>> {
  const { data } = await apiClient.get(`${PRODUCTS_ENDPOINT}/by-sku/${sku}/`);
  return data;
}

async function getProductByBarcode(barcode: string): Promise<APIResponse<Product>> {
  const { data } = await apiClient.get(`${PRODUCTS_ENDPOINT}/by-barcode/${barcode}/`);
  return data;
}

async function createProduct(
  productData: ProductCreateRequest
): Promise<APIResponse<Product>> {
  const { data } = await apiClient.post(`${PRODUCTS_ENDPOINT}/`, productData);
  return data;
}

async function updateProduct(
  id: string,
  productData: ProductUpdateRequest
): Promise<APIResponse<Product>> {
  const { data } = await apiClient.patch(`${PRODUCTS_ENDPOINT}/${id}/`, productData);
  return data;
}

async function deleteProduct(id: string): Promise<APIResponse<void>> {
  const { data } = await apiClient.delete(`${PRODUCTS_ENDPOINT}/${id}/`);
  return data;
}

async function bulkUpdateProducts(
  operation: ProductBulkOperation
): Promise<APIResponse<number>> {
  const { data } = await apiClient.post(`${PRODUCTS_ENDPOINT}/bulk/`, operation);
  return data;
}

async function bulkDeleteProducts(
  productIds: string[]
): Promise<APIResponse<number>> {
  const { data } = await apiClient.delete(`${PRODUCTS_ENDPOINT}/bulk/`, {
    data: { productIds },
  });
  return data;
}

// ── Variant Operations ─────────────────────────────────────────

async function getProductVariants(
  productId: string
): Promise<APIResponse<ProductVariant[]>> {
  const { data } = await apiClient.get(
    `${PRODUCTS_ENDPOINT}/${productId}/variants/`
  );
  return data;
}

async function createProductVariant(
  productId: string,
  variantData: Partial<ProductVariant>
): Promise<APIResponse<ProductVariant>> {
  const { data } = await apiClient.post(
    `${PRODUCTS_ENDPOINT}/${productId}/variants/`,
    variantData
  );
  return data;
}

async function updateProductVariant(
  productId: string,
  variantId: string,
  variantData: Partial<ProductVariant>
): Promise<APIResponse<ProductVariant>> {
  const { data } = await apiClient.patch(
    `${PRODUCTS_ENDPOINT}/${productId}/variants/${variantId}/`,
    variantData
  );
  return data;
}

async function deleteProductVariant(
  productId: string,
  variantId: string
): Promise<APIResponse<void>> {
  const { data } = await apiClient.delete(
    `${PRODUCTS_ENDPOINT}/${productId}/variants/${variantId}/`
  );
  return data;
}

// ── Image Operations ───────────────────────────────────────────

async function uploadProductImage(
  productId: string,
  file: File,
  isPrimary?: boolean
): Promise<APIResponse<ProductImage>> {
  const formData = new FormData();
  formData.append('image', file);
  if (isPrimary) formData.append('isPrimary', 'true');

  const { data } = await apiClient.post(
    `${PRODUCTS_ENDPOINT}/${productId}/images/`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  );
  return data;
}

async function reorderProductImages(
  productId: string,
  imageOrder: string[]
): Promise<APIResponse<void>> {
  const { data } = await apiClient.put(
    `${PRODUCTS_ENDPOINT}/${productId}/images/reorder/`,
    { imageOrder }
  );
  return data;
}

async function deleteProductImage(
  productId: string,
  imageId: string
): Promise<APIResponse<void>> {
  const { data } = await apiClient.delete(
    `${PRODUCTS_ENDPOINT}/${productId}/images/${imageId}/`
  );
  return data;
}

// ── Availability ───────────────────────────────────────────────

async function checkProductAvailability(
  productId: string,
  quantity: number,
  warehouseId?: string
): Promise<APIResponse<boolean>> {
  const { data } = await apiClient.get(
    `${PRODUCTS_ENDPOINT}/${productId}/availability/`,
    { params: { quantity, warehouseId } }
  );
  return data;
}

const productService = {
  getProducts,
  getProductById,
  getProductBySku,
  getProductByBarcode,
  createProduct,
  updateProduct,
  deleteProduct,
  bulkUpdateProducts,
  bulkDeleteProducts,
  getProductVariants,
  createProductVariant,
  updateProductVariant,
  deleteProductVariant,
  uploadProductImage,
  reorderProductImages,
  deleteProductImage,
  checkProductAvailability,
};

export default productService;
