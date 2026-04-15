/** Store customer profile */
export interface StoreCustomer {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  phone?: string;
  addresses?: StoreAddress[];
  defaultAddressId?: string;
  createdAt: Date;
}

/** Customer address */
export interface StoreAddress {
  id: string;
  label?: string;
  firstName: string;
  lastName: string;
  addressLine1: string;
  addressLine2?: string;
  city: string;
  province: string;
  postalCode: string;
  country: string;
  phone?: string;
  isDefault: boolean;
}

/** Auth state */
export interface StoreAuthState {
  customer: StoreCustomer | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isGuest: boolean;
}

/** Auth context value exposed via useStoreAuth */
export interface StoreAuthContextValue extends StoreAuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  register: (data: RegisterData) => Promise<void>;
  updateProfile: (updates: Partial<StoreCustomer>) => Promise<void>;
  refreshToken: () => Promise<void>;
}

/** Login credentials */
export interface LoginCredentials {
  email: string;
  password: string;
}

/** Registration data */
export interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  phone?: string;
}
