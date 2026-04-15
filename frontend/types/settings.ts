export interface GeneralSettings {
  timezone: string;
  currency: string;
  dateFormat: string;
  emailNotifications: boolean;
  pushNotifications: boolean;
  orderAlerts: boolean;
  inventoryAlerts: boolean;
  marketingEmails: boolean;
}

export interface CompanyAddress {
  street: string;
  city: string;
  province: string;
  postalCode: string;
  country: string;
}

export interface CompanySettings {
  name: string;
  logo?: string;
  address: CompanyAddress;
  tin?: string;
  vatNumber?: string;
  taxRegistrationType?: string;
  phone: string;
  email: string;
  website?: string;
}

export interface TenantUser {
  id: string;
  name: string;
  email: string;
  role: string;
  status: 'ACTIVE' | 'PENDING' | 'DISABLED';
  lastLogin?: string;
  createdAt: string;
  avatarUrl?: string;
}

export interface UserInvitation {
  id: string;
  email: string;
  role: string;
  status: 'PENDING' | 'ACCEPTED' | 'EXPIRED';
  sentAt: string;
  expiresAt: string;
}

export interface Role {
  id: string;
  name: string;
  description?: string;
  permissions: string[];
  userCount: number;
  isSystem: boolean;
  createdAt: string;
}

export interface Permission {
  id: string;
  name: string;
  description?: string;
  group: string;
}

export interface Integration {
  id: string;
  name: string;
  description: string;
  category: 'payment' | 'communication' | 'business' | 'other';
  status: 'CONNECTED' | 'DISCONNECTED';
  icon?: string;
  configUrl?: string;
  lastSync?: string;
}

export interface APIKey {
  id: string;
  name: string;
  key: string;
  prefix: string;
  createdAt: string;
  lastUsedAt?: string;
  expiresAt?: string;
  status: 'ACTIVE' | 'REVOKED';
}

export interface SubscriptionPlan {
  id: string;
  name: string;
  price: number;
  currency: string;
  interval: 'monthly' | 'yearly';
  features: string[];
  maxUsers: number;
  maxProducts: number;
  isCurrent: boolean;
}

export interface BillingInvoice {
  id: string;
  date: string;
  amount: number;
  currency: string;
  status: 'PAID' | 'PENDING' | 'FAILED';
  downloadUrl?: string;
}

export interface PaymentMethod {
  id: string;
  type: 'card' | 'bank';
  last4: string;
  brand?: string;
  expiryMonth?: number;
  expiryYear?: number;
  isDefault: boolean;
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  userId: string;
  userName: string;
  action:
    | 'CREATE'
    | 'UPDATE'
    | 'DELETE'
    | 'LOGIN'
    | 'LOGOUT'
    | 'PERMISSION'
    | 'SETTINGS'
    | 'SYSTEM';
  entity: string;
  entityId?: string;
  details: string;
  ipAddress?: string;
}
