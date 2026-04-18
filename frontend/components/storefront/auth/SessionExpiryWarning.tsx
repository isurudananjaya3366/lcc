'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { AlertTriangle } from 'lucide-react';
import { useTokenRefresh } from '@/hooks/storefront/useTokenRefresh';
import { useStoreAuthStore } from '@/stores/store';
import { clearTokens } from '@/services/storefront/tokenService';
import { cn } from '@/lib/cn';

export function SessionExpiryWarning() {
  const { isExpiringSoon, refreshToken } = useTokenRefresh();
  const isAuthenticated = useStoreAuthStore((s) => s.isAuthenticated);
  const logout = useStoreAuthStore((s) => s.logout);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  // Reset dismissed state when warning reappears
  useEffect(() => {
    if (!isExpiringSoon) {
      setDismissed(false);
    }
  }, [isExpiringSoon]);

  const handleStaySignedIn = async () => {
    setIsRefreshing(true);
    try {
      await refreshToken();
      setDismissed(true);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleSignOut = () => {
    clearTokens();
    logout();
  };

  if (!isAuthenticated || !isExpiringSoon || dismissed) {
    return null;
  }

  return (
    <div
      className={cn(
        'fixed bottom-4 right-4 z-50 w-full max-w-sm rounded-lg border bg-background p-4 shadow-lg',
        'animate-in slide-in-from-bottom-5 fade-in duration-300'
      )}
      role="alert"
    >
      <div className="flex items-start gap-3">
        <AlertTriangle className="h-5 w-5 shrink-0 text-amber-500" />
        <div className="flex-1 space-y-2">
          <p className="text-sm font-medium">Session Expiring Soon</p>
          <p className="text-xs text-muted-foreground">
            Your session is about to expire. Would you like to stay signed in?
          </p>
          <div className="flex gap-2 pt-1">
            <Button
              size="sm"
              onClick={handleStaySignedIn}
              disabled={isRefreshing}
            >
              {isRefreshing ? 'Refreshing…' : 'Stay Signed In'}
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={handleSignOut}
            >
              Sign Out
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
