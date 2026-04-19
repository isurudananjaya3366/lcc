'use client';

import { useEffect, useRef } from 'react';
import { Bell } from 'lucide-react';
import type { FlashSale } from '@/types/marketing/flash-sale.types';

interface SaleEndNotificationProps {
  sale: FlashSale;
  onClose?: () => void;
  className?: string;
}

/**
 * Toast/banner shown when a flash sale ends while the user is on the page.
 * Typically rendered by a parent that detects sale.status === 'ended'.
 */
export function SaleEndNotification({ sale, onClose, className = '' }: SaleEndNotificationProps) {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    timerRef.current = setTimeout(() => {
      onClose?.();
    }, 8000);
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [onClose]);

  return (
    <div
      role="alert"
      aria-live="assertive"
      className={`fixed bottom-6 left-1/2 z-50 flex w-full max-w-sm -translate-x-1/2 items-start gap-3 rounded-xl bg-gray-900 px-4 py-3 text-white shadow-2xl ${className}`}
    >
      <Bell className="mt-0.5 h-5 w-5 flex-shrink-0 text-yellow-400" />
      <div className="flex-1">
        <p className="text-sm font-semibold">Flash sale has ended</p>
        <p className="mt-0.5 text-xs text-gray-300">&ldquo;{sale.title}&rdquo; is no longer available.</p>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          type="button"
          className="ml-2 flex-shrink-0 rounded p-0.5 text-gray-400 hover:text-white"
          aria-label="Dismiss notification"
        >
          ✕
        </button>
      )}
    </div>
  );
}
