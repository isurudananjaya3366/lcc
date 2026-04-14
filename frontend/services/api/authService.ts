/**
 * Authentication Service
 *
 * Handles all authentication-related API calls including login, logout,
 * token refresh, user profile retrieval, and password management.
 */

import apiClient from './apiClient';
import { setAccessToken, setRefreshToken, clearTokens, getRefreshToken } from '@/lib/tokenStorage';
import type {
  LoginRequest,
  LoginResponse,
  RefreshTokenResponse,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  ChangePasswordRequest,
  VerifyEmailRequest,
  VerifyEmailResponse,
  ResendVerificationRequest,
  TwoFactorSetupResponse,
  TwoFactorVerifySetupRequest,
  TwoFactorVerifySetupResponse,
  TwoFactorVerifyLoginRequest,
  TwoFactorVerifyBackupCodeRequest,
  TwoFactorVerifyResponse,
  User,
} from '@/types/auth';

// ── API Endpoints ──────────────────────────────────────────────

const AUTH_ENDPOINTS = {
  LOGIN: '/auth/login',
  LOGOUT: '/auth/logout',
  REFRESH: '/auth/refresh',
  ME: '/auth/me',
  FORGOT_PASSWORD: '/auth/forgot-password',
  RESET_PASSWORD: '/auth/reset-password',
  CHANGE_PASSWORD: '/auth/change-password',
  VERIFY_EMAIL: '/auth/verify-email',
  RESEND_VERIFICATION: '/auth/resend-verification',
  TWO_FACTOR_SETUP: '/auth/2fa/setup',
  TWO_FACTOR_VERIFY_SETUP: '/auth/2fa/verify-setup',
  TWO_FACTOR_VERIFY: '/auth/2fa/verify',
  TWO_FACTOR_BACKUP: '/auth/2fa/backup-verify',
} as const;

// ── Auth Service ───────────────────────────────────────────────

export const authService = {
  /**
   * Authenticate user with email and password.
   * Stores tokens on successful login.
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>(AUTH_ENDPOINTS.LOGIN, credentials);
    const data = response.data;
    setAccessToken(data.accessToken);
    setRefreshToken(data.refreshToken);
    return data;
  },

  /**
   * Log out the current user.
   * Clears tokens regardless of API response.
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post(AUTH_ENDPOINTS.LOGOUT);
    } finally {
      clearTokens();
    }
  },

  /**
   * Refresh the access token using the stored refresh token.
   * Updates the stored access token on success.
   */
  async refreshToken(): Promise<RefreshTokenResponse> {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      clearTokens();
      throw new Error('No refresh token available');
    }

    const response = await apiClient.post<RefreshTokenResponse>(AUTH_ENDPOINTS.REFRESH, {
      refreshToken,
    });
    const data = response.data;
    setAccessToken(data.accessToken);
    return data;
  },

  /**
   * Retrieve the current authenticated user's profile.
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>(AUTH_ENDPOINTS.ME);
    return response.data;
  },

  /**
   * Request a password reset email.
   */
  async forgotPassword(data: ForgotPasswordRequest): Promise<void> {
    await apiClient.post(AUTH_ENDPOINTS.FORGOT_PASSWORD, data);
  },

  /**
   * Reset password using a token from the reset email.
   */
  async resetPassword(data: ResetPasswordRequest): Promise<void> {
    await apiClient.post(AUTH_ENDPOINTS.RESET_PASSWORD, data);
  },

  /**
   * Change the current user's password (requires authentication).
   */
  async changePassword(data: ChangePasswordRequest): Promise<void> {
    await apiClient.post(AUTH_ENDPOINTS.CHANGE_PASSWORD, data);
  },

  /**
   * Verify email address using token from verification email.
   */
  async verifyEmail(data: VerifyEmailRequest): Promise<VerifyEmailResponse> {
    const response = await apiClient.post<VerifyEmailResponse>(AUTH_ENDPOINTS.VERIFY_EMAIL, data);
    return response.data;
  },

  /**
   * Resend email verification link.
   */
  async resendVerification(data: ResendVerificationRequest): Promise<void> {
    await apiClient.post(AUTH_ENDPOINTS.RESEND_VERIFICATION, data);
  },

  /**
   * Initialize 2FA setup — returns secret and QR code URL.
   */
  async setup2FA(): Promise<TwoFactorSetupResponse> {
    const response = await apiClient.post<TwoFactorSetupResponse>(AUTH_ENDPOINTS.TWO_FACTOR_SETUP);
    return response.data;
  },

  /**
   * Verify OTP during 2FA setup to confirm authenticator is configured.
   */
  async verify2FASetup(data: TwoFactorVerifySetupRequest): Promise<TwoFactorVerifySetupResponse> {
    const response = await apiClient.post<TwoFactorVerifySetupResponse>(
      AUTH_ENDPOINTS.TWO_FACTOR_VERIFY_SETUP,
      data
    );
    return response.data;
  },

  /**
   * Verify OTP during login when 2FA is enabled.
   */
  async verify2FALogin(data: TwoFactorVerifyLoginRequest): Promise<TwoFactorVerifyResponse> {
    const response = await apiClient.post<TwoFactorVerifyResponse>(
      AUTH_ENDPOINTS.TWO_FACTOR_VERIFY,
      data
    );
    const result = response.data;
    setAccessToken(result.accessToken);
    setRefreshToken(result.refreshToken);
    return result;
  },

  /**
   * Verify backup code during login when 2FA is enabled.
   */
  async verify2FABackupCode(
    data: TwoFactorVerifyBackupCodeRequest
  ): Promise<TwoFactorVerifyResponse> {
    const response = await apiClient.post<TwoFactorVerifyResponse>(
      AUTH_ENDPOINTS.TWO_FACTOR_BACKUP,
      data
    );
    const result = response.data;
    setAccessToken(result.accessToken);
    setRefreshToken(result.refreshToken);
    return result;
  },
};

export default authService;
