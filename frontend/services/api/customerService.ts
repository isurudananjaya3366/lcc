/**
 * Customer Service
 *
 * Type-safe CRUD operations for customers, addresses, contacts,
 * credit management, loyalty programs, and transaction history.
 */

import { apiClient } from './apiClient';
import type { APIResponse, PaginatedResponse } from '@/types/api';
import type {
  Customer,
  CustomerCreateRequest,
  CustomerUpdateRequest,
  CustomerSearchParams,
  CustomerAddress,
  CustomerContact,
  CustomerCreditLimit,
  CustomerTransaction,
  CustomerStatement,
  CustomerLoyalty,
  CustomerNote,
} from '@/types/customer';

const CUSTOMER_ENDPOINT = '/api/v1/customers';

// ── Customer CRUD ──────────────────────────────────────────────

async function getCustomers(
  params?: CustomerSearchParams
): Promise<PaginatedResponse<Customer>> {
  const { data } = await apiClient.get(`${CUSTOMER_ENDPOINT}/`, { params });
  return data;
}

async function getCustomerById(id: string): Promise<APIResponse<Customer>> {
  const { data } = await apiClient.get(`${CUSTOMER_ENDPOINT}/${id}/`);
  return data;
}

async function getCustomerByNumber(
  customerNumber: string
): Promise<APIResponse<Customer>> {
  const { data } = await apiClient.get(
    `${CUSTOMER_ENDPOINT}/by-number/${customerNumber}/`
  );
  return data;
}

async function getCustomerByEmail(
  email: string
): Promise<APIResponse<Customer>> {
  const { data } = await apiClient.get(
    `${CUSTOMER_ENDPOINT}/by-email/${encodeURIComponent(email)}/`
  );
  return data;
}

async function createCustomer(
  customerData: CustomerCreateRequest
): Promise<APIResponse<Customer>> {
  const { data } = await apiClient.post(`${CUSTOMER_ENDPOINT}/`, customerData);
  return data;
}

async function updateCustomer(
  id: string,
  customerData: CustomerUpdateRequest
): Promise<APIResponse<Customer>> {
  const { data } = await apiClient.patch(`${CUSTOMER_ENDPOINT}/${id}/`, customerData);
  return data;
}

async function deleteCustomer(id: string): Promise<APIResponse<void>> {
  const { data } = await apiClient.delete(`${CUSTOMER_ENDPOINT}/${id}/`);
  return data;
}

// ── Address Management ─────────────────────────────────────────

async function getCustomerAddresses(
  customerId: string
): Promise<APIResponse<CustomerAddress[]>> {
  const { data } = await apiClient.get(`${CUSTOMER_ENDPOINT}/${customerId}/addresses/`);
  return data;
}

async function createCustomerAddress(
  customerId: string,
  addressData: Omit<CustomerAddress, 'id' | 'customerId'>
): Promise<APIResponse<CustomerAddress>> {
  const { data } = await apiClient.post(
    `${CUSTOMER_ENDPOINT}/${customerId}/addresses/`,
    addressData
  );
  return data;
}

async function updateCustomerAddress(
  customerId: string,
  addressId: string,
  addressData: Partial<CustomerAddress>
): Promise<APIResponse<CustomerAddress>> {
  const { data } = await apiClient.patch(
    `${CUSTOMER_ENDPOINT}/${customerId}/addresses/${addressId}/`,
    addressData
  );
  return data;
}

async function deleteCustomerAddress(
  customerId: string,
  addressId: string
): Promise<APIResponse<void>> {
  const { data } = await apiClient.delete(
    `${CUSTOMER_ENDPOINT}/${customerId}/addresses/${addressId}/`
  );
  return data;
}

async function setDefaultAddress(
  customerId: string,
  addressId: string,
  addressType: 'BILLING' | 'SHIPPING'
): Promise<APIResponse<void>> {
  const { data } = await apiClient.post(
    `${CUSTOMER_ENDPOINT}/${customerId}/addresses/${addressId}/set-default/`,
    { addressType }
  );
  return data;
}

// ── Contact Management ─────────────────────────────────────────

async function getCustomerContacts(
  customerId: string
): Promise<APIResponse<CustomerContact[]>> {
  const { data } = await apiClient.get(`${CUSTOMER_ENDPOINT}/${customerId}/contacts/`);
  return data;
}

async function createCustomerContact(
  customerId: string,
  contactData: Omit<CustomerContact, 'id' | 'customerId'>
): Promise<APIResponse<CustomerContact>> {
  const { data } = await apiClient.post(
    `${CUSTOMER_ENDPOINT}/${customerId}/contacts/`,
    contactData
  );
  return data;
}

async function updateCustomerContact(
  customerId: string,
  contactId: string,
  contactData: Partial<CustomerContact>
): Promise<APIResponse<CustomerContact>> {
  const { data } = await apiClient.patch(
    `${CUSTOMER_ENDPOINT}/${customerId}/contacts/${contactId}/`,
    contactData
  );
  return data;
}

async function deleteCustomerContact(
  customerId: string,
  contactId: string
): Promise<APIResponse<void>> {
  const { data } = await apiClient.delete(
    `${CUSTOMER_ENDPOINT}/${customerId}/contacts/${contactId}/`
  );
  return data;
}

// ── Credit Management ──────────────────────────────────────────

async function getCustomerCreditInfo(
  customerId: string
): Promise<APIResponse<CustomerCreditLimit>> {
  const { data } = await apiClient.get(`${CUSTOMER_ENDPOINT}/${customerId}/credit/`);
  return data;
}

async function updateCustomerCredit(
  customerId: string,
  creditData: Partial<CustomerCreditLimit>
): Promise<APIResponse<CustomerCreditLimit>> {
  const { data } = await apiClient.patch(
    `${CUSTOMER_ENDPOINT}/${customerId}/credit/`,
    creditData
  );
  return data;
}

// ── Transaction History ────────────────────────────────────────

async function getCustomerTransactions(
  customerId: string,
  params?: { startDate?: string; endDate?: string; transactionType?: string }
): Promise<PaginatedResponse<CustomerTransaction>> {
  const { data } = await apiClient.get(
    `${CUSTOMER_ENDPOINT}/${customerId}/transactions/`,
    { params }
  );
  return data;
}

async function getCustomerStatement(
  customerId: string,
  startDate: string,
  endDate: string
): Promise<APIResponse<CustomerStatement>> {
  const { data } = await apiClient.get(
    `${CUSTOMER_ENDPOINT}/${customerId}/statement/`,
    { params: { startDate, endDate } }
  );
  return data;
}

async function recordCustomerPayment(
  customerId: string,
  paymentData: {
    amount: number;
    paymentMethod: string;
    referenceId?: string;
    notes?: string;
  }
): Promise<APIResponse<CustomerTransaction>> {
  const { data } = await apiClient.post(
    `${CUSTOMER_ENDPOINT}/${customerId}/payments/`,
    paymentData
  );
  return data;
}

// ── Loyalty Program ────────────────────────────────────────────

async function getCustomerLoyalty(
  customerId: string
): Promise<APIResponse<CustomerLoyalty>> {
  const { data } = await apiClient.get(`${CUSTOMER_ENDPOINT}/${customerId}/loyalty/`);
  return data;
}

async function addLoyaltyPoints(
  customerId: string,
  points: number,
  referenceType: string,
  referenceId: string
): Promise<APIResponse<CustomerLoyalty>> {
  const { data } = await apiClient.post(
    `${CUSTOMER_ENDPOINT}/${customerId}/loyalty/add-points/`,
    { points, referenceType, referenceId }
  );
  return data;
}

async function redeemLoyaltyPoints(
  customerId: string,
  points: number,
  redemptionType: string
): Promise<APIResponse<CustomerLoyalty>> {
  const { data } = await apiClient.post(
    `${CUSTOMER_ENDPOINT}/${customerId}/loyalty/redeem-points/`,
    { points, redemptionType }
  );
  return data;
}

// ── Notes ──────────────────────────────────────────────────────

async function addCustomerNote(
  customerId: string,
  note: string,
  category?: string,
  isPrivate?: boolean
): Promise<APIResponse<CustomerNote>> {
  const { data } = await apiClient.post(
    `${CUSTOMER_ENDPOINT}/${customerId}/notes/`,
    { note, category, isPrivate }
  );
  return data;
}

async function getCustomerNotes(
  customerId: string
): Promise<APIResponse<CustomerNote[]>> {
  const { data } = await apiClient.get(`${CUSTOMER_ENDPOINT}/${customerId}/notes/`);
  return data;
}

const customerService = {
  getCustomers,
  getCustomerById,
  getCustomerByNumber,
  getCustomerByEmail,
  createCustomer,
  updateCustomer,
  deleteCustomer,
  getCustomerAddresses,
  createCustomerAddress,
  updateCustomerAddress,
  deleteCustomerAddress,
  setDefaultAddress,
  getCustomerContacts,
  createCustomerContact,
  updateCustomerContact,
  deleteCustomerContact,
  getCustomerCreditInfo,
  updateCustomerCredit,
  getCustomerTransactions,
  getCustomerStatement,
  recordCustomerPayment,
  getCustomerLoyalty,
  addLoyaltyPoints,
  redeemLoyaltyPoints,
  addCustomerNote,
  getCustomerNotes,
};

export default customerService;
