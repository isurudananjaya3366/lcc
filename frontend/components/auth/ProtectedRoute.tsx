'use client';

import { useEffect, useState, useMemo, type ReactNode } from 'react';
import { useRouter, usePathname } from 'next/navigation';

import { useAuthStore } from '@/stores/useAuthStore';
import { getAccessToken, isTokenExpired } from '@/lib/tokenStorage';
import { AuthLoading } from '@/components/auth/AuthLoading';

export interface ProtectedRouteProps {
  children: ReactNode;
  requiredPermissions?: string[];
  requireAll?: boolean;
  fallback?: ReactNode;
}

const INTENDED_URL_KEY = 'lcc_intended_url';

export function ProtectedRoute({
  children,
  requiredPermissions = [],
  requireAll = false,
  fallback,
}: ProtectedRouteProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, isLoading, user, canAccess } = useAuthStore();
  const [isChecking, setIsChecking] = useState(true);

  const hasRequiredPermissions = useMemo(() => {
    if (requiredPermissions.length === 0) return true;
    return canAccess(requiredPermissions, requireAll ? 'all' : 'any');
  }, [canAccess, requiredPermissions, requireAll]);

  useEffect(() => {
    // Wait for auth store to finish hydrating
    if (isLoading) return;

    const token = getAccessToken();
    const tokenValid = !isTokenExpired(token);

    if (!isAuthenticated || !user || !tokenValid) {
      // Store intended URL for post-login redirect
      try {
        if (pathname && pathname !== '/login') {
          sessionStorage.setItem(INTENDED_URL_KEY, pathname);
        }
      } catch {
        // sessionStorage unavailable
      }
      router.replace('/login');
      return;
    }

    if (requiredPermissions.length > 0 && !hasRequiredPermissions) {
      router.replace('/unauthorized');
      return;
    }

    setIsChecking(false);
  }, [
    isAuthenticated,
    isLoading,
    user,
    hasRequiredPermissions,
    requiredPermissions.length,
    router,
    pathname,
  ]);

  if (isLoading || isChecking) {
    return fallback ?? <AuthLoading fullScreen message="Verifying access..." />;
  }

  return <>{children}</>;
}

/**
 * Retrieve and clear the stored intended URL after login.
 */
export function getIntendedUrl(): string | null {
  try {
    const url = sessionStorage.getItem(INTENDED_URL_KEY);
    if (url) {
      sessionStorage.removeItem(INTENDED_URL_KEY);
      // Basic validation — only allow relative paths
      if (url.startsWith('/') && !url.startsWith('//')) {
        return url;
      }
    }
  } catch {
    // sessionStorage unavailable
  }
  return null;
}
