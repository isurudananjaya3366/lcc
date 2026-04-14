/**
 * Quote type definitions for the Sales module
 */

export type QuoteStatus = 'draft' | 'sent' | 'accepted' | 'rejected' | 'expired' | 'converted';

export interface QuoteItem {
  id: string;
  productId: string;
  productName: string;
  sku: string;
  variantId?: string;
  quantity: number;
  unitPrice: number;
  discountPercent: number;
  total: number;
}

export interface Quote {
  id: string;
  quoteNumber: string;
  customerId: string;
  customerName: string;
  customerEmail?: string;
  status: QuoteStatus;
  quoteDate: string;
  expiryDate: string;
  items: QuoteItem[];
  subtotal: number;
  discountTotal: number;
  taxTotal: number;
  total: number;
  terms?: string;
  notes?: string;
  orderId?: string;
  createdBy?: string;
  createdAt: string;
  updatedAt: string;
}

export interface QuoteSearchParams {
  search?: string;
  status?: QuoteStatus | 'all';
  customerId?: string;
  startDate?: string;
  endDate?: string;
  page?: number;
  limit?: number;
}

export interface QuoteCreateRequest {
  customerId: string;
  expiryDate: string;
  items: {
    productId: string;
    variantId?: string;
    quantity: number;
    unitPrice: number;
    discountPercent?: number;
  }[];
  terms?: string;
  notes?: string;
}

export interface QuoteConversionRequest {
  quoteId: string;
  generateInvoice: boolean;
  sendEmail: boolean;
  applyDiscount: boolean;
  orderNotes?: string;
}
