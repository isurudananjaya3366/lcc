/**
 * Authentication Type Definitions
 *
 * Types for JWT authentication flow including user profile,
 * login/logout, token refresh, and password management.
 */

// ── User Types ─────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
  permissions: string[];
  avatar?: string;
  phone?: string;
  lastLogin?: string;
  tenantId?: string;
}

// ── Auth Request Types ─────────────────────────────────────────

export interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RefreshTokenRequest {
  refreshToken: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  newPassword: string;
  confirmPassword: string;
}

export interface ChangePasswordRequest {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

// ── Auth Response Types ────────────────────────────────────────

export interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  user: User;
  expiresIn?: number;
}

export interface RefreshTokenResponse {
  accessToken: string;
  expiresIn?: number;
}

export interface AuthResponse<T = void> {
  success: boolean;
  message?: string;
  data?: T;
}

// ── Email Verification Types ───────────────────────────────────

export interface VerifyEmailRequest {
  token: string;
}

export interface VerifyEmailResponse {
  success: boolean;
  message: string;
  email?: string;
}

export interface ResendVerificationRequest {
  email: string;
}

// ── 2FA Types ──────────────────────────────────────────────────

export interface TwoFactorSetupResponse {
  secret: string;
  qrCodeUrl: string;
  otpauthUrl: string;
}

export interface TwoFactorVerifySetupRequest {
  otp: string;
}

export interface TwoFactorVerifySetupResponse {
  success: boolean;
  backupCodes: string[];
}

export interface TwoFactorVerifyLoginRequest {
  otp: string;
  sessionToken: string;
}

export interface TwoFactorVerifyBackupCodeRequest {
  backupCode: string;
  sessionToken: string;
}

export interface TwoFactorVerifyResponse {
  accessToken: string;
  refreshToken: string;
  user: User;
}
