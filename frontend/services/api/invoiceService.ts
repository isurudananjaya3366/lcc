/**
 * Invoice Service
 *
 * Type-safe operations for invoices — create from order, send,
 * record payment, void, download PDF, and overdue tracking.
 */

import { apiClient } from './apiClient';
import type { APIResponse, PaginatedResponse, PaginationParams } from '@/types/api';

// ── Local Types ────────────────────────────────────────────────

export enum InvoiceStatus {
  DRAFT = 'draft',
  SENT = 'sent',
  PAID = 'paid',
  PARTIALLY_PAID = 'partially_paid',
  OVERDUE = 'overdue',
  VOID = 'void',
  CANCELLED = 'cancelled',
}

export interface InvoiceLineItem {
  id: string;
  productId: string;
  productName: string;
  sku: string;
  quantity: number;
  unitPrice: number;
  discount: number;
  taxRate: number;
  taxAmount: number;
  lineTotal: number;
}

export interface Invoice {
  id: string;
  invoiceNumber: string;
  orderId: string;
  orderNumber: string;
  customerId: string;
  customerName: string;
  status: InvoiceStatus;
  items: InvoiceLineItem[];
  subtotal: number;
  taxTotal: number;
  discountTotal: number;
  total: number;
  amountPaid: number;
  balanceDue: number;
  issueDate: string;
  dueDate: string;
  paidDate?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface InvoiceSearchParams extends PaginationParams {
  status?: InvoiceStatus;
  customerId?: string;
  startDate?: string;
  endDate?: string;
  overdue?: boolean;
}

const INVOICE_ENDPOINT = '/api/v1/invoices';

// ── Invoice Operations ─────────────────────────────────────────

async function getInvoices(
  params?: InvoiceSearchParams
): Promise<PaginatedResponse<Invoice>> {
  const { data } = await apiClient.get(`${INVOICE_ENDPOINT}/`, { params });
  return data;
}

async function getInvoiceById(id: string): Promise<APIResponse<Invoice>> {
  const { data } = await apiClient.get(`${INVOICE_ENDPOINT}/${id}/`);
  return data;
}

async function createInvoiceFromOrder(
  orderId: string,
  dueDate?: string
): Promise<APIResponse<Invoice>> {
  const { data } = await apiClient.post(`${INVOICE_ENDPOINT}/`, {
    orderId,
    dueDate,
  });
  return data;
}

async function sendInvoice(
  id: string,
  email?: string
): Promise<APIResponse<Invoice>> {
  const { data } = await apiClient.post(`${INVOICE_ENDPOINT}/${id}/send/`, {
    email,
  });
  return data;
}

async function recordPayment(
  id: string,
  payment: { amount: number; method: string; reference?: string; date?: string }
): Promise<APIResponse<Invoice>> {
  const { data } = await apiClient.post(
    `${INVOICE_ENDPOINT}/${id}/payments/`,
    payment
  );
  return data;
}

async function voidInvoice(
  id: string,
  reason: string
): Promise<APIResponse<Invoice>> {
  const { data } = await apiClient.post(`${INVOICE_ENDPOINT}/${id}/void/`, {
    reason,
  });
  return data;
}

async function downloadInvoicePdf(id: string): Promise<Blob> {
  const { data } = await apiClient.get(`${INVOICE_ENDPOINT}/${id}/pdf/`, {
    responseType: 'blob',
  });
  return data;
}

async function getOverdueInvoices(): Promise<PaginatedResponse<Invoice>> {
  const { data } = await apiClient.get(`${INVOICE_ENDPOINT}/overdue/`);
  return data;
}

async function sendReminder(
  id: string,
  email?: string
): Promise<APIResponse<{ sent: boolean }>> {
  const { data } = await apiClient.post(`${INVOICE_ENDPOINT}/${id}/reminder/`, {
    email,
  });
  return data;
}

async function getInvoiceSummary(params?: {
  startDate?: string;
  endDate?: string;
}): Promise<
  APIResponse<{
    totalInvoiced: number;
    totalPaid: number;
    totalOutstanding: number;
    totalOverdue: number;
    invoiceCount: number;
  }>
> {
  const { data } = await apiClient.get(`${INVOICE_ENDPOINT}/summary/`, { params });
  return data;
}

const invoiceService = {
  getInvoices,
  getInvoiceById,
  createInvoiceFromOrder,
  sendInvoice,
  recordPayment,
  voidInvoice,
  downloadInvoicePdf,
  getOverdueInvoices,
  sendReminder,
  getInvoiceSummary,
};

export default invoiceService;
