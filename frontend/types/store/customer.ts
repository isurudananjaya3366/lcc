/**
 * Storefront Customer Types
 */

export interface StoreCustomer {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  phone: string;
  avatar?: string;
  status: 'active' | 'inactive' | 'suspended';
  emailVerified: boolean;
  phoneVerified: boolean;
  addresses: StoreCustomerAddress[];
  preferences: StoreCustomerPreferences;
  createdAt: string;
  updatedAt?: string;
}

export interface StoreCustomerAddress {
  id: string;
  type: 'billing' | 'shipping' | 'other';
  firstName: string;
  lastName: string;
  line1: string;
  line2?: string;
  city: string;
  province: SriLankanProvince;
  postalCode: string;
  country: string;
  phone: string;
  isDefault: boolean;
}

export enum SriLankanProvince {
  WESTERN = 'Western',
  CENTRAL = 'Central',
  SOUTHERN = 'Southern',
  EASTERN = 'Eastern',
  NORTHERN = 'Northern',
  NORTH_WESTERN = 'North Western',
  NORTH_CENTRAL = 'North Central',
  UVA = 'Uva',
  SABARAGAMUWA = 'Sabaragamuwa',
}

export interface StoreCustomerPreferences {
  language: 'en-LK' | 'si-LK';
  currency: 'LKR';
  theme?: 'light' | 'dark';
  notifications: boolean;
}

export interface StoreAuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: string;
}

export interface StoreCustomerAuth {
  customer: StoreCustomer;
  tokens: StoreAuthTokens;
  lastLogin?: string;
}
