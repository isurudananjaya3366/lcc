'use client';

import { useRouter } from 'next/navigation';
import { useCallback } from 'react';

import { useSessionMonitor } from '@/hooks/useSessionMonitor';
import { useAuthStore } from '@/stores/useAuthStore';
import { SessionExpiryModal } from './SessionExpiryModal';

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, logout } = useAuthStore();
  const { sessionStatus, timeUntilExpiry, refreshSession } = useSessionMonitor();

  const handleLogout = useCallback(() => {
    logout();
    router.replace('/login?reason=session_expired');
  }, [logout, router]);

  const handleExtend = useCallback(() => {
    refreshSession();
  }, [refreshSession]);

  return (
    <>
      {children}
      {isAuthenticated && (
        <SessionExpiryModal
          isOpen={sessionStatus === 'expiring' || sessionStatus === 'expired'}
          expiryType={sessionStatus === 'expired' ? 'expired' : 'warning'}
          timeRemaining={Math.max(0, Math.floor(timeUntilExpiry / 1000))}
          onExtendSession={handleExtend}
          onLogout={handleLogout}
        />
      )}
    </>
  );
}
