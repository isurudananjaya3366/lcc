'use client';

import { X, ShoppingBag } from 'lucide-react';
import { useExitIntent } from '@/hooks/marketing/useExitIntent';

interface ExitIntentPopupProps {
  title?: string;
  description?: string;
  couponCode?: string;
  actionLabel?: string;
  actionUrl?: string;
  className?: string;
}

export function ExitIntentPopup({
  title = "Wait! Don't leave yet",
  description = "Here's a special discount just for you!",
  couponCode,
  actionLabel = 'Continue Shopping',
  actionUrl = '/',
  className = '',
}: ExitIntentPopupProps) {
  const { triggered, reset } = useExitIntent();

  if (!triggered) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 p-4">
      <div className={`relative w-full max-w-sm overflow-hidden rounded-2xl bg-white shadow-2xl ${className}`}>
        <button
          onClick={reset}
          className="absolute right-3 top-3 rounded-full p-1.5 hover:bg-gray-100"
          type="button"
          aria-label="Close"
        >
          <X className="h-5 w-5 text-gray-500" />
        </button>

        <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-6 text-center text-white">
          <ShoppingBag className="mx-auto mb-3 h-10 w-10" />
          <h3 className="text-xl font-bold">{title}</h3>
          <p className="mt-1 text-sm text-blue-100">{description}</p>
        </div>

        <div className="p-6 text-center">
          {couponCode && (
            <div className="mb-4 rounded-lg border-2 border-dashed border-blue-300 bg-blue-50 px-4 py-3">
              <p className="text-xs text-gray-500">Use code</p>
              <p className="text-lg font-bold tracking-wider text-blue-700">{couponCode}</p>
            </div>
          )}

          <a
            href={actionUrl}
            onClick={reset}
            className="inline-block w-full rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
          >
            {actionLabel}
          </a>
          <button onClick={reset} className="mt-2 text-sm text-gray-500 hover:text-gray-700" type="button">
            No thanks
          </button>
        </div>
      </div>
    </div>
  );
}
