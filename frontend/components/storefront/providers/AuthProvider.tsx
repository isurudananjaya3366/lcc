'use client';

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
  type FC,
} from 'react';
import type {
  StoreCustomer,
  StoreAuthState,
  StoreAuthContextValue,
  LoginCredentials,
  RegisterData,
} from '@/types/store-auth';

const TOKEN_KEY = 'store-auth-token';
const GUEST_KEY = 'store-guest-id';

const StoreAuthContext = createContext<StoreAuthContextValue | null>(null);

export interface StoreAuthProviderProps {
  children: ReactNode;
  tokenKey?: string;
}

/**
 * Authentication provider for storefront customers.
 * Manages login/logout, registration, guest users, and token refresh.
 * Separate from the ERP dashboard authentication.
 */
const AuthProvider: FC<StoreAuthProviderProps> = ({ children, tokenKey = TOKEN_KEY }) => {
  const [state, setState] = useState<StoreAuthState>({
    customer: null,
    isAuthenticated: false,
    isLoading: true,
    isGuest: true,
  });

  // Initialize auth state from stored token
  useEffect(() => {
    try {
      const token = localStorage.getItem(tokenKey);
      if (token) {
        // TODO: Validate token with backend API and fetch customer data
        // For now, just mark as loading complete
        setState((prev) => ({ ...prev, isLoading: false }));
      } else {
        // Ensure guest ID exists
        if (!localStorage.getItem(GUEST_KEY)) {
          localStorage.setItem(GUEST_KEY, crypto.randomUUID());
        }
        setState((prev) => ({ ...prev, isLoading: false }));
      }
    } catch {
      setState((prev) => ({ ...prev, isLoading: false }));
    }
  }, [tokenKey]);

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      setState((prev) => ({ ...prev, isLoading: true }));
      try {
        // TODO: Replace with actual API call — POST /api/store/auth/login
        const response = await fetch('/api/store/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(credentials),
        });
        if (!response.ok) {
          throw new Error('Login failed');
        }
        const data = await response.json();
        localStorage.setItem(tokenKey, data.token);
        setState({
          customer: data.customer,
          isAuthenticated: true,
          isLoading: false,
          isGuest: false,
        });
      } catch (error) {
        setState((prev) => ({ ...prev, isLoading: false }));
        throw error;
      }
    },
    [tokenKey]
  );

  const logout = useCallback(() => {
    localStorage.removeItem(tokenKey);
    // Keep guest ID for cart continuity
    if (!localStorage.getItem(GUEST_KEY)) {
      localStorage.setItem(GUEST_KEY, crypto.randomUUID());
    }
    setState({
      customer: null,
      isAuthenticated: false,
      isLoading: false,
      isGuest: true,
    });
  }, [tokenKey]);

  const register = useCallback(
    async (data: RegisterData) => {
      setState((prev) => ({ ...prev, isLoading: true }));
      try {
        // TODO: Replace with actual API call — POST /api/store/auth/register
        const response = await fetch('/api/store/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
        if (!response.ok) {
          throw new Error('Registration failed');
        }
        const result = await response.json();
        localStorage.setItem(tokenKey, result.token);
        localStorage.removeItem(GUEST_KEY);
        setState({
          customer: result.customer,
          isAuthenticated: true,
          isLoading: false,
          isGuest: false,
        });
      } catch (error) {
        setState((prev) => ({ ...prev, isLoading: false }));
        throw error;
      }
    },
    [tokenKey]
  );

  const updateProfile = useCallback(async (updates: Partial<StoreCustomer>) => {
    setState((prev) => ({
      ...prev,
      customer: prev.customer ? { ...prev.customer, ...updates } : null,
    }));
    // TODO: API call to update profile
  }, []);

  const refreshToken = useCallback(async () => {
    try {
      // TODO: Replace with actual API call — POST /api/store/auth/refresh
      const response = await fetch('/api/store/auth/refresh', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem(tokenKey)}`,
        },
      });
      if (!response.ok) {
        logout();
        return;
      }
      const data = await response.json();
      localStorage.setItem(tokenKey, data.token);
    } catch {
      logout();
    }
  }, [tokenKey, logout]);

  const value: StoreAuthContextValue = {
    ...state,
    login,
    logout,
    register,
    updateProfile,
    refreshToken,
  };

  return <StoreAuthContext.Provider value={value}>{children}</StoreAuthContext.Provider>;
};

export function useStoreAuth(): StoreAuthContextValue {
  const ctx = useContext(StoreAuthContext);
  if (!ctx) {
    throw new Error('useStoreAuth must be used within an AuthProvider');
  }
  return ctx;
}

export default AuthProvider;
