'use client';

import { useEffect, useState, useCallback } from 'react';
import { Clock, AlertCircle, Loader2 } from 'lucide-react';

export interface SessionExpiryModalProps {
  isOpen: boolean;
  expiryType: 'warning' | 'expired';
  timeRemaining?: number;
  onExtendSession: () => void;
  onLogout: () => void;
}

const AUTO_LOGOUT_SECONDS = 30;

function formatTime(seconds: number): string {
  if (seconds <= 0) return '0 seconds';
  const min = Math.floor(seconds / 60);
  const sec = seconds % 60;
  if (min > 0) {
    return `${min} minute${min !== 1 ? 's' : ''} ${sec} second${sec !== 1 ? 's' : ''}`;
  }
  return `${sec} second${sec !== 1 ? 's' : ''}`;
}

export function SessionExpiryModal({
  isOpen,
  expiryType,
  timeRemaining = 0,
  onExtendSession,
  onLogout,
}: SessionExpiryModalProps) {
  const [countdown, setCountdown] = useState(timeRemaining);
  const [autoLogoutCountdown, setAutoLogoutCountdown] = useState(AUTO_LOGOUT_SECONDS);
  const [isExtending, setIsExtending] = useState(false);

  // Update warning countdown
  useEffect(() => {
    if (!isOpen || expiryType !== 'warning') return;
    setCountdown(timeRemaining);

    const interval = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isOpen, expiryType, timeRemaining]);

  // Auto-logout countdown for expired state
  useEffect(() => {
    if (!isOpen || expiryType !== 'expired') return;
    setAutoLogoutCountdown(AUTO_LOGOUT_SECONDS);

    const interval = setInterval(() => {
      setAutoLogoutCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          onLogout();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isOpen, expiryType, onLogout]);

  const handleExtend = useCallback(async () => {
    setIsExtending(true);
    try {
      onExtendSession();
    } finally {
      setIsExtending(false);
    }
  }, [onExtendSession]);

  if (!isOpen) return null;

  const isWarning = expiryType === 'warning';

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      role="dialog"
      aria-modal="true"
      aria-label={isWarning ? 'Session expiring warning' : 'Session expired'}
    >
      <div className="mx-4 w-full max-w-md rounded-xl bg-white p-6 shadow-2xl">
        {/* Header */}
        <div className="flex flex-col items-center gap-3 text-center">
          {isWarning ? (
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-amber-100">
              <Clock className="h-7 w-7 text-amber-600" />
            </div>
          ) : (
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-red-100">
              <AlertCircle className="h-7 w-7 text-red-600" />
            </div>
          )}
          <h2 className="text-lg font-semibold text-gray-900">
            {isWarning ? 'Session Expiring' : 'Session Expired'}
          </h2>
        </div>

        {/* Content */}
        <div className="mt-4 text-center text-sm text-gray-600">
          {isWarning ? (
            <>
              <p>
                Your session is about to expire in{' '}
                <span className="font-semibold text-amber-700">{formatTime(countdown)}</span>.
              </p>
              <p className="mt-2">
                Please extend your session or you will be automatically logged out to protect your
                account.
              </p>
            </>
          ) : (
            <>
              <p>Your session has expired for security reasons.</p>
              <p className="mt-2">Please log in again to continue.</p>
              <p className="mt-3 text-xs text-gray-400">
                Auto logout in {autoLogoutCountdown} seconds...
              </p>
            </>
          )}
        </div>

        {/* Actions */}
        <div className="mt-6 flex gap-3">
          {isWarning ? (
            <>
              <button
                type="button"
                onClick={handleExtend}
                disabled={isExtending}
                className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
              >
                {isExtending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Extending...
                  </>
                ) : (
                  'Extend Session'
                )}
              </button>
              <button
                type="button"
                onClick={onLogout}
                className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
              >
                Logout
              </button>
            </>
          ) : (
            <button
              type="button"
              onClick={onLogout}
              className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700"
            >
              Login Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
