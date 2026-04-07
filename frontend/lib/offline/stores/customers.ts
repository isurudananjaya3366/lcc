// ================================================================
// Customers Object Store — Task 22
// ================================================================
// CRUD + search for the local customers cache.
// ================================================================

import { idbService } from '../indexeddb';
import { ObjectStoreNames, type Customer } from '../schema';

const STORE = ObjectStoreNames.CUSTOMERS;

class CustomersService {
  async addCustomer(customer: Customer): Promise<void> {
    if (!customer.email && !customer.phone) {
      throw new Error('Customer must have at least an email or phone number.');
    }
    await idbService.put(STORE, customer);
  }

  async getCustomer(customerId: string): Promise<Customer | undefined> {
    return idbService.get<Customer>(STORE, customerId);
  }

  async getAllCustomers(): Promise<Customer[]> {
    return idbService.getAll<Customer>(STORE);
  }

  async getCustomerByPhone(phone: string): Promise<Customer | undefined> {
    const normalised = this.normalizePhoneNumber(phone);
    return idbService.getByIndex<Customer>(STORE, 'phone', normalised);
  }

  async getCustomerByEmail(email: string): Promise<Customer | undefined> {
    const normalised = this.normalizeEmail(email);
    return idbService.getByIndex<Customer>(STORE, 'email', normalised);
  }

  async searchCustomers(term: string): Promise<Customer[]> {
    const lower = term.toLowerCase();
    const all = await this.getAllCustomers();
    return all.filter(
      (c) =>
        c.name.toLowerCase().includes(lower) ||
        c.email?.toLowerCase().includes(lower) ||
        c.phone?.includes(term)
    );
  }

  async bulkAddCustomers(customers: Customer[]): Promise<number> {
    return idbService.bulkPut(STORE, customers);
  }

  async updateCustomer(
    customerId: string,
    updates: Partial<Customer>
  ): Promise<void> {
    const existing = await this.getCustomer(customerId);
    if (!existing) throw new Error(`Customer ${customerId} not found`);
    await idbService.put(STORE, {
      ...existing,
      ...updates,
      updated_at: new Date().toISOString(),
    });
  }

  async deleteCustomer(customerId: string): Promise<void> {
    await idbService.delete(STORE, customerId);
  }

  async updateCustomerLoyalty(
    customerId: string,
    pointsDelta: number
  ): Promise<void> {
    const customer = await this.getCustomer(customerId);
    if (!customer) throw new Error(`Customer ${customerId} not found`);
    customer.loyalty_points += pointsDelta;
    customer.updated_at = new Date().toISOString();
    await idbService.put(STORE, customer);
  }

  async getCustomerCount(): Promise<number> {
    return idbService.count(STORE);
  }

  async getMostRecentUpdate(): Promise<string | null> {
    const all = await this.getAllCustomers();
    if (all.length === 0) return null;
    return all.reduce(
      (latest, c) => (c.updated_at > latest ? c.updated_at : latest),
      all[0]!.updated_at
    );
  }

  // ── Phone / email normalization ──────────────────────────────

  /** Normalize Sri Lankan phone numbers to +94 format. */
  normalizePhoneNumber(phone: string): string {
    const digits = phone.replace(/\D/g, '');
    if (digits.startsWith('94') && digits.length >= 11) return `+${digits}`;
    if (digits.startsWith('0') && digits.length === 10)
      return `+94${digits.slice(1)}`;
    return phone; // return as-is if format unknown
  }

  normalizeEmail(email: string): string {
    return email.trim().toLowerCase();
  }
}

export const customersService = new CustomersService();
