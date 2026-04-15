'use client';

import React, { type ReactNode, type FC } from 'react';
import ThemeProvider from './ThemeProvider';
import AuthProvider from './AuthProvider';
import CartProvider from './CartProvider';

export interface StoreProvidersProps {
  children: ReactNode;
  initialTheme?: 'light' | 'dark';
}

/**
 * Centralized provider wrapper for all storefront contexts.
 * Composes theme, auth, cart, and notification providers.
 *
 * Provider hierarchy:
 * ThemeProvider → StoreAuthProvider → CartProvider → children
 */
const StoreProviders: FC<StoreProvidersProps> = ({ children, initialTheme = 'light' }) => {
  return (
    <ThemeProvider defaultTheme={initialTheme}>
      <AuthProvider>
        <CartProvider>{children}</CartProvider>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default StoreProviders;
