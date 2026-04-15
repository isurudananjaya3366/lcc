import { getStoreClient } from '../client';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface Customer {
  id: number;
  email: string;
  phone: string;
  username: string;
  first_name: string;
  last_name: string;
  date_of_birth: string | null;
  gender: 'M' | 'F' | 'Other' | null;
  avatar_url: string | null;
  is_verified: boolean;
}

export interface CustomerAddress {
  id: number;
  customer_id: number;
  full_name: string;
  phone: string;
  address_line1: string;
  address_line2: string | null;
  city: string;
  district: string;
  province: string;
  postal_code: string;
  country: string;
  is_default: boolean;
  address_type: 'shipping' | 'billing' | 'home' | 'work';
}

export interface CustomerPreferences {
  language: 'en' | 'si' | 'ta';
  currency: string;
  timezone: string;
  notifications: NotificationSettings;
  marketing_consent: boolean;
}

export interface NotificationSettings {
  order_updates: boolean;
  promotions: boolean;
  newsletters: boolean;
  wishlist_reminders: boolean;
  back_in_stock_alerts: boolean;
}

export interface UserProfile extends Customer {
  preferences: CustomerPreferences;
  addresses: CustomerAddress[];
  statistics: {
    total_orders: number;
    total_spent: number;
    member_since: string;
  };
  created_at: string;
  updated_at: string;
}

export interface UpdateProfileParams {
  first_name?: string;
  last_name?: string;
  phone?: string;
  date_of_birth?: string;
  gender?: 'M' | 'F' | 'Other';
}

export interface AddAddressParams {
  full_name: string;
  phone: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  district: string;
  province: string;
  postal_code: string;
  country?: string;
  address_type: 'shipping' | 'billing' | 'home' | 'work';
  is_default?: boolean;
}

// ─── Sri Lankan Validation ──────────────────────────────────────────────────

const SL_PHONE_REGEX = /^\+94[0-9]{9}$/;
const SL_OPERATOR_CODES = ['70', '71', '72', '74', '75', '76', '77', '78'];

export const SL_DISTRICTS = [
  'Ampara',
  'Anuradhapura',
  'Badulla',
  'Batticaloa',
  'Colombo',
  'Galle',
  'Gampaha',
  'Hambantota',
  'Jaffna',
  'Kalutara',
  'Kandy',
  'Kegalle',
  'Kilinochchi',
  'Kurunegala',
  'Mannar',
  'Matale',
  'Matara',
  'Monaragala',
  'Mullaitivu',
  'Nuwara Eliya',
  'Polonnaruwa',
  'Puttalam',
  'Ratnapura',
  'Trincomalee',
  'Vavuniya',
] as const;

export const SL_PROVINCES = [
  'Central',
  'Eastern',
  'North Central',
  'Northern',
  'North Western',
  'Sabaragamuwa',
  'Southern',
  'Uva',
  'Western',
] as const;

export function validatePhoneNumber(phone: string): boolean {
  if (!SL_PHONE_REGEX.test(phone)) return false;
  const operatorCode = phone.substring(3, 5);
  return SL_OPERATOR_CODES.includes(operatorCode);
}

export function formatPhoneNumber(phone: string): string {
  const digits = phone.replace(/\D/g, '');
  if (digits.startsWith('94') && digits.length === 11) {
    return `+${digits.slice(0, 2)} ${digits.slice(2, 4)} ${digits.slice(4, 7)} ${digits.slice(7)}`;
  }
  if (digits.startsWith('0') && digits.length === 10) {
    return `+94 ${digits.slice(1, 3)} ${digits.slice(3, 6)} ${digits.slice(6)}`;
  }
  return phone;
}

export function validateDistrict(district: string): boolean {
  return (SL_DISTRICTS as readonly string[]).includes(district);
}

export function validateProvince(province: string): boolean {
  return (SL_PROVINCES as readonly string[]).includes(province);
}

export function formatAddressForDisplay(address: CustomerAddress): string {
  const lines = [address.address_line1];
  if (address.address_line2) lines.push(address.address_line2);
  lines.push(`${address.city}, ${address.district}`);
  lines.push(`${address.province} Province`);
  lines.push(address.postal_code);
  lines.push('Sri Lanka');
  return lines.join('\n');
}

export function getFullName(customer: Customer): string {
  return `${customer.first_name} ${customer.last_name}`.trim();
}

export function getInitials(customer: Customer): string {
  const first = customer.first_name?.[0] || '';
  const last = customer.last_name?.[0] || '';
  return `${first}${last}`.toUpperCase();
}

export function getCustomerTier(totalSpent: number): 'Bronze' | 'Silver' | 'Gold' | 'Platinum' {
  if (totalSpent >= 500000) return 'Platinum';
  if (totalSpent >= 200000) return 'Gold';
  if (totalSpent >= 50000) return 'Silver';
  return 'Bronze';
}

export function hasCompleteProfile(profile: UserProfile): boolean {
  return !!(
    profile.first_name &&
    profile.last_name &&
    profile.email &&
    profile.phone &&
    profile.addresses.length > 0
  );
}

// ─── API Functions ──────────────────────────────────────────────────────────

export async function getCurrentUser(): Promise<UserProfile> {
  const { data } = await getStoreClient().get('/customer/me/');
  return data;
}

export async function updateProfile(params: UpdateProfileParams): Promise<UserProfile> {
  const { data } = await getStoreClient().put('/customer/me/', params);
  return data;
}

export async function getAddresses(type?: 'shipping' | 'billing'): Promise<CustomerAddress[]> {
  const { data } = await getStoreClient().get('/customer/me/addresses/', {
    params: type ? { type } : undefined,
  });
  return data.results ?? data;
}

export async function addAddress(params: AddAddressParams): Promise<CustomerAddress> {
  const { data } = await getStoreClient().post('/customer/me/addresses/', {
    ...params,
    country: params.country || 'LK',
  });
  return data;
}

export async function updateAddress(
  addressId: number,
  params: Partial<AddAddressParams>
): Promise<CustomerAddress> {
  const { data } = await getStoreClient().put(`/customer/me/addresses/${addressId}/`, params);
  return data;
}

export async function deleteAddress(addressId: number): Promise<void> {
  await getStoreClient().delete(`/customer/me/addresses/${addressId}/`);
}

export async function setDefaultAddress(
  addressId: number,
  type: 'shipping' | 'billing'
): Promise<CustomerAddress> {
  const { data } = await getStoreClient().put(`/customer/me/addresses/${addressId}/set-default/`, {
    type,
  });
  return data;
}

export async function updatePreferences(
  preferences: Partial<CustomerPreferences>
): Promise<CustomerPreferences> {
  const { data } = await getStoreClient().put('/customer/me/preferences/', preferences);
  return data;
}

export async function updateNotificationSettings(
  settings: Partial<NotificationSettings>
): Promise<NotificationSettings> {
  const { data } = await getStoreClient().put('/customer/me/notification-settings/', settings);
  return data;
}

const customerApi = {
  getCurrentUser,
  updateProfile,
  getAddresses,
  addAddress,
  updateAddress,
  deleteAddress,
  setDefaultAddress,
  updatePreferences,
  updateNotificationSettings,
  validatePhoneNumber,
  formatPhoneNumber,
  validateDistrict,
  validateProvince,
  formatAddressForDisplay,
  getFullName,
  getInitials,
  getCustomerTier,
  hasCompleteProfile,
};

export default customerApi;
