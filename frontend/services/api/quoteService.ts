/**
 * Quote Service
 *
 * Type-safe operations for quotes — CRUD, send, convert to order.
 */

import { apiClient } from './apiClient';
import type { APIResponse, PaginatedResponse } from '@/types/api';
import type {
  Quote,
  QuoteSearchParams,
  QuoteCreateRequest,
  QuoteConversionRequest,
} from '@/types/quotes';

const QUOTE_ENDPOINT = '/api/v1/quotes';

async function getQuotes(params?: QuoteSearchParams): Promise<PaginatedResponse<Quote>> {
  const { data } = await apiClient.get(`${QUOTE_ENDPOINT}/`, { params });
  return data;
}

async function getQuoteById(id: string): Promise<APIResponse<Quote>> {
  const { data } = await apiClient.get(`${QUOTE_ENDPOINT}/${id}/`);
  return data;
}

async function createQuote(payload: QuoteCreateRequest): Promise<APIResponse<Quote>> {
  const { data } = await apiClient.post(`${QUOTE_ENDPOINT}/`, payload);
  return data;
}

async function updateQuote(
  id: string,
  payload: Partial<QuoteCreateRequest>
): Promise<APIResponse<Quote>> {
  const { data } = await apiClient.patch(`${QUOTE_ENDPOINT}/${id}/`, payload);
  return data;
}

async function deleteQuote(id: string): Promise<void> {
  await apiClient.delete(`${QUOTE_ENDPOINT}/${id}/`);
}

async function sendQuote(id: string, email?: string): Promise<APIResponse<Quote>> {
  const { data } = await apiClient.post(`${QUOTE_ENDPOINT}/${id}/send/`, {
    email,
  });
  return data;
}

async function convertToOrder(
  payload: QuoteConversionRequest
): Promise<APIResponse<{ orderId: string; orderNumber: string }>> {
  const { data } = await apiClient.post(`${QUOTE_ENDPOINT}/${payload.quoteId}/convert/`, payload);
  return data;
}

export const quoteService = {
  getQuotes,
  getQuoteById,
  createQuote,
  updateQuote,
  deleteQuote,
  sendQuote,
  convertToOrder,
};
