'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';

export interface CookieConsentData {
  accepted: boolean;
  categories: {
    necessary: boolean;
    analytics: boolean;
    marketing: boolean;
    preferences: boolean;
  };
  timestamp: number;
  expiresAt: number;
  version: string;
}

export interface CookieConsentProps {
  privacyPolicyUrl?: string;
  cookiePolicyUrl?: string;
  onAccept?: () => void;
  onReject?: () => void;
}

const STORAGE_KEY = 'lcc-cookie-consent';
const EXPIRY_MS = 365 * 24 * 60 * 60 * 1000; // 365 days
const CONSENT_VERSION = '1.0';

function getStoredConsent(): CookieConsentData | null {
  if (typeof window === 'undefined') return null;
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return null;
    const consent: CookieConsentData = JSON.parse(stored);
    if (consent.expiresAt < Date.now()) {
      localStorage.removeItem(STORAGE_KEY);
      return null;
    }
    return consent;
  } catch {
    return null;
  }
}

function storeConsent(consent: CookieConsentData): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(consent));
  } catch {
    // Storage may be full or disabled
  }
}

export function CookieConsent({
  privacyPolicyUrl = '/privacy',
  cookiePolicyUrl = '/cookies',
  onAccept,
  onReject,
}: CookieConsentProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const existing = getStoredConsent();
    if (!existing) {
      setIsVisible(true);
    }
  }, []);

  const handleAccept = useCallback(() => {
    const consent: CookieConsentData = {
      accepted: true,
      categories: {
        necessary: true,
        analytics: true,
        marketing: true,
        preferences: true,
      },
      timestamp: Date.now(),
      expiresAt: Date.now() + EXPIRY_MS,
      version: CONSENT_VERSION,
    };
    storeConsent(consent);
    setIsVisible(false);
    onAccept?.();
  }, [onAccept]);

  const handleReject = useCallback(() => {
    const consent: CookieConsentData = {
      accepted: false,
      categories: {
        necessary: true,
        analytics: false,
        marketing: false,
        preferences: false,
      },
      timestamp: Date.now(),
      expiresAt: Date.now() + EXPIRY_MS,
      version: CONSENT_VERSION,
    };
    storeConsent(consent);
    setIsVisible(false);
    onReject?.();
  }, [onReject]);

  if (!isVisible) return null;

  return (
    <div
      className={cn(
        'fixed inset-x-0 bottom-0 z-50',
        'border-t border-gray-700 bg-gray-800 text-white shadow-2xl',
        'animate-in slide-in-from-bottom duration-500'
      )}
      role="dialog"
      aria-label="Cookie consent"
    >
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 md:flex-row md:items-center md:px-6">
        {/* Message */}
        <div className="flex-1 text-sm text-gray-300">
          <p>
            We use cookies to enhance your browsing experience, serve personalized content, and
            analyze our traffic. By clicking &quot;Accept All&quot;, you consent to our use of
            cookies.{' '}
            <Link href={privacyPolicyUrl} className="text-blue-400 underline hover:text-blue-300">
              Privacy Policy
            </Link>
            {' · '}
            <Link href={cookiePolicyUrl} className="text-blue-400 underline hover:text-blue-300">
              Cookie Settings
            </Link>
          </p>
        </div>

        {/* Actions */}
        <div className="flex shrink-0 items-center gap-3">
          <button
            type="button"
            onClick={handleReject}
            className={cn(
              'rounded-lg border border-gray-500 px-4 py-2 text-sm font-medium text-gray-300',
              'transition-colors hover:border-gray-400 hover:text-white',
              'focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 focus:ring-offset-gray-800'
            )}
          >
            Reject
          </button>
          <button
            type="button"
            onClick={handleAccept}
            className={cn(
              'rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white',
              'transition-colors hover:bg-blue-500',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800'
            )}
          >
            Accept All
          </button>
        </div>
      </div>
    </div>
  );
}

export default CookieConsent;
