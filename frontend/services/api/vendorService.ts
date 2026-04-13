/**
 * Vendor Service
 *
 * Type-safe CRUD operations for vendors, contacts, purchase orders,
 * invoices, payments, and performance tracking.
 */

import { apiClient } from './apiClient';
import type { APIResponse, PaginatedResponse } from '@/types/api';
import type {
  Vendor,
  VendorCreateRequest,
  VendorUpdateRequest,
  VendorSearchParams,
  VendorContact,
  VendorProduct,
  PurchaseOrder,
  VendorInvoice,
  VendorPayment,
  VendorPerformance,
} from '@/types/vendor';

const VENDOR_ENDPOINT = '/api/v1/vendors';
const PO_ENDPOINT = '/api/v1/purchase-orders';
const VENDOR_INVOICE_ENDPOINT = '/api/v1/vendor-invoices';
const VENDOR_PAYMENT_ENDPOINT = '/api/v1/vendor-payments';

// ── Vendor CRUD ────────────────────────────────────────────────

async function getVendors(
  params?: VendorSearchParams
): Promise<PaginatedResponse<Vendor>> {
  const { data } = await apiClient.get(`${VENDOR_ENDPOINT}/`, { params });
  return data;
}

async function getVendorById(id: string): Promise<APIResponse<Vendor>> {
  const { data } = await apiClient.get(`${VENDOR_ENDPOINT}/${id}/`);
  return data;
}

async function getVendorByNumber(
  vendorNumber: string
): Promise<APIResponse<Vendor>> {
  const { data } = await apiClient.get(
    `${VENDOR_ENDPOINT}/by-number/${vendorNumber}/`
  );
  return data;
}

async function createVendor(
  vendorData: VendorCreateRequest
): Promise<APIResponse<Vendor>> {
  const { data } = await apiClient.post(`${VENDOR_ENDPOINT}/`, vendorData);
  return data;
}

async function updateVendor(
  id: string,
  vendorData: VendorUpdateRequest
): Promise<APIResponse<Vendor>> {
  const { data } = await apiClient.patch(`${VENDOR_ENDPOINT}/${id}/`, vendorData);
  return data;
}

async function deleteVendor(id: string): Promise<APIResponse<void>> {
  const { data } = await apiClient.delete(`${VENDOR_ENDPOINT}/${id}/`);
  return data;
}

// ── Vendor Contacts ────────────────────────────────────────────

async function getVendorContacts(
  vendorId: string
): Promise<APIResponse<VendorContact[]>> {
  const { data } = await apiClient.get(`${VENDOR_ENDPOINT}/${vendorId}/contacts/`);
  return data;
}

async function createVendorContact(
  vendorId: string,
  contactData: Omit<VendorContact, 'id' | 'vendorId'>
): Promise<APIResponse<VendorContact>> {
  const { data } = await apiClient.post(
    `${VENDOR_ENDPOINT}/${vendorId}/contacts/`,
    contactData
  );
  return data;
}

async function updateVendorContact(
  vendorId: string,
  contactId: string,
  contactData: Partial<VendorContact>
): Promise<APIResponse<VendorContact>> {
  const { data } = await apiClient.patch(
    `${VENDOR_ENDPOINT}/${vendorId}/contacts/${contactId}/`,
    contactData
  );
  return data;
}

async function deleteVendorContact(
  vendorId: string,
  contactId: string
): Promise<APIResponse<void>> {
  const { data } = await apiClient.delete(
    `${VENDOR_ENDPOINT}/${vendorId}/contacts/${contactId}/`
  );
  return data;
}

// ── Vendor Products ────────────────────────────────────────────

async function getVendorProducts(
  vendorId: string
): Promise<PaginatedResponse<VendorProduct>> {
  const { data } = await apiClient.get(`${VENDOR_ENDPOINT}/${vendorId}/products/`);
  return data;
}

async function addVendorProduct(
  vendorId: string,
  productData: Omit<VendorProduct, 'id' | 'vendorId'>
): Promise<APIResponse<VendorProduct>> {
  const { data } = await apiClient.post(
    `${VENDOR_ENDPOINT}/${vendorId}/products/`,
    productData
  );
  return data;
}

async function updateVendorProduct(
  vendorId: string,
  vendorProductId: string,
  productData: Partial<VendorProduct>
): Promise<APIResponse<VendorProduct>> {
  const { data } = await apiClient.patch(
    `${VENDOR_ENDPOINT}/${vendorId}/products/${vendorProductId}/`,
    productData
  );
  return data;
}

async function removeVendorProduct(
  vendorId: string,
  vendorProductId: string
): Promise<APIResponse<void>> {
  const { data } = await apiClient.delete(
    `${VENDOR_ENDPOINT}/${vendorId}/products/${vendorProductId}/`
  );
  return data;
}

// ── Purchase Orders ────────────────────────────────────────────

async function getPurchaseOrders(params?: {
  vendorId?: string;
  status?: string;
  startDate?: string;
  endDate?: string;
}): Promise<PaginatedResponse<PurchaseOrder>> {
  const { data } = await apiClient.get(`${PO_ENDPOINT}/`, { params });
  return data;
}

async function getPurchaseOrderById(
  id: string
): Promise<APIResponse<PurchaseOrder>> {
  const { data } = await apiClient.get(`${PO_ENDPOINT}/${id}/`);
  return data;
}

async function createPurchaseOrder(
  poData: Omit<PurchaseOrder, 'id' | 'poNumber' | 'createdAt'>
): Promise<APIResponse<PurchaseOrder>> {
  const { data } = await apiClient.post(`${PO_ENDPOINT}/`, poData);
  return data;
}

async function updatePurchaseOrder(
  id: string,
  poData: Partial<PurchaseOrder>
): Promise<APIResponse<PurchaseOrder>> {
  const { data } = await apiClient.patch(`${PO_ENDPOINT}/${id}/`, poData);
  return data;
}

async function receivePurchaseOrder(
  id: string,
  receivedItems: { itemId: string; quantityReceived: number }[]
): Promise<APIResponse<PurchaseOrder>> {
  const { data } = await apiClient.post(`${PO_ENDPOINT}/${id}/receive/`, {
    receivedItems,
  });
  return data;
}

async function cancelPurchaseOrder(
  id: string,
  reason: string
): Promise<APIResponse<PurchaseOrder>> {
  const { data } = await apiClient.post(`${PO_ENDPOINT}/${id}/cancel/`, { reason });
  return data;
}

// ── Vendor Invoices ────────────────────────────────────────────

async function getVendorInvoices(
  vendorId: string,
  params?: { status?: string; startDate?: string; endDate?: string }
): Promise<PaginatedResponse<VendorInvoice>> {
  const { data } = await apiClient.get(
    `${VENDOR_ENDPOINT}/${vendorId}/invoices/`,
    { params }
  );
  return data;
}

async function createVendorInvoice(
  invoiceData: Omit<VendorInvoice, 'id' | 'createdAt'>
): Promise<APIResponse<VendorInvoice>> {
  const { data } = await apiClient.post(`${VENDOR_INVOICE_ENDPOINT}/`, invoiceData);
  return data;
}

// ── Vendor Payments ────────────────────────────────────────────

async function recordVendorPayment(
  paymentData: Omit<VendorPayment, 'id' | 'paymentNumber' | 'createdAt'>
): Promise<APIResponse<VendorPayment>> {
  const { data } = await apiClient.post(`${VENDOR_PAYMENT_ENDPOINT}/`, paymentData);
  return data;
}

async function getVendorPayments(
  vendorId: string,
  params?: { startDate?: string; endDate?: string }
): Promise<PaginatedResponse<VendorPayment>> {
  const { data } = await apiClient.get(
    `${VENDOR_ENDPOINT}/${vendorId}/payments/`,
    { params }
  );
  return data;
}

// ── Performance & Balance ──────────────────────────────────────

async function getVendorPerformance(
  vendorId: string,
  period?: string
): Promise<APIResponse<VendorPerformance>> {
  const { data } = await apiClient.get(
    `${VENDOR_ENDPOINT}/${vendorId}/performance/`,
    { params: period ? { period } : undefined }
  );
  return data;
}

async function getVendorBalance(
  vendorId: string
): Promise<APIResponse<{ totalPayable: number; overdue: number; current: number }>> {
  const { data } = await apiClient.get(`${VENDOR_ENDPOINT}/${vendorId}/balance/`);
  return data;
}

const vendorService = {
  getVendors,
  getVendorById,
  getVendorByNumber,
  createVendor,
  updateVendor,
  deleteVendor,
  getVendorContacts,
  createVendorContact,
  updateVendorContact,
  deleteVendorContact,
  getVendorProducts,
  addVendorProduct,
  updateVendorProduct,
  removeVendorProduct,
  getPurchaseOrders,
  getPurchaseOrderById,
  createPurchaseOrder,
  updatePurchaseOrder,
  receivePurchaseOrder,
  cancelPurchaseOrder,
  getVendorInvoices,
  createVendorInvoice,
  recordVendorPayment,
  getVendorPayments,
  getVendorPerformance,
  getVendorBalance,
};

export default vendorService;
