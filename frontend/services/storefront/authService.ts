import type {
  StoreUser,
  LoginCredentials,
  RegisterFormData,
  ForgotPasswordData,
  ResetPasswordData,
  OTPVerifyData,
} from '@/types/storefront/auth.types';

// ─── Config ─────────────────────────────────────────────────────────────────

const API_BASE = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/store/auth`;

// ─── Helpers ────────────────────────────────────────────────────────────────

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || body.message || `Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

// ─── API Functions ──────────────────────────────────────────────────────────

/** Authenticate with email + password. Returns user profile. */
export async function loginApi(
  email: string,
  password: string
): Promise<{ user: StoreUser }> {
  const res = await fetch(`${API_BASE}/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ email, password }),
  });
  return handleResponse<{ user: StoreUser }>(res);
}

/** Register a new customer account. */
export async function registerApi(
  data: Omit<RegisterFormData, 'confirmPassword' | 'termsAccepted'>
): Promise<{ user: StoreUser }> {
  const res = await fetch(`${API_BASE}/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(data),
  });
  return handleResponse<{ user: StoreUser }>(res);
}

/** Log out the current session. */
export async function logoutApi(): Promise<void> {
  await fetch(`${API_BASE}/logout/`, {
    method: 'POST',
    credentials: 'include',
  });
}

/** Fetch the currently authenticated user. */
export async function getCurrentUser(): Promise<{ user: StoreUser }> {
  const res = await fetch(`${API_BASE}/me/`, {
    method: 'GET',
    credentials: 'include',
  });
  return handleResponse<{ user: StoreUser }>(res);
}

/** Request a password-reset email. */
export async function requestPasswordReset(
  email: string
): Promise<{ message: string }> {
  const res = await fetch(`${API_BASE}/forgot-password/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ email } satisfies ForgotPasswordData),
  });
  return handleResponse<{ message: string }>(res);
}

/** Verify an OTP code. */
export async function verifyOTP(
  data: OTPVerifyData
): Promise<{ verified: boolean }> {
  const res = await fetch(`${API_BASE}/verify-otp/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(data),
  });
  return handleResponse<{ verified: boolean }>(res);
}

/** Reset password with token. */
export async function resetPassword(
  data: ResetPasswordData
): Promise<{ message: string }> {
  const res = await fetch(`${API_BASE}/reset-password/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(data),
  });
  return handleResponse<{ message: string }>(res);
}

/** Refresh the auth token / session. */
export async function refreshTokenApi(): Promise<{ user: StoreUser }> {
  const res = await fetch(`${API_BASE}/refresh/`, {
    method: 'POST',
    credentials: 'include',
  });
  return handleResponse<{ user: StoreUser }>(res);
}
