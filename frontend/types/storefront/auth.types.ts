// ─── Storefront Auth Types ──────────────────────────────────────────────────

/** Authenticated store user profile */
export interface StoreUser {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  phone?: string;
  createdAt: string;
}

/** Login credentials */
export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

/** Registration form data */
export interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
  phone?: string;
  termsAccepted: boolean;
}

/** Forgot password request */
export interface ForgotPasswordData {
  email: string;
}

/** Reset password request */
export interface ResetPasswordData {
  token: string;
  email: string;
  password: string;
  confirmPassword: string;
}

/** OTP verification */
export interface OTPVerifyData {
  otp: string;
  email: string;
  phone?: string;
}

/** Auth state shape */
export interface AuthState {
  user: StoreUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
