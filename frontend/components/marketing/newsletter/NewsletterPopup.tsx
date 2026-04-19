'use client';

import { X, Mail } from 'lucide-react';
import type { PopupConfig } from '@/types/marketing/popup.types';
import { usePopupTrigger } from '@/hooks/marketing/usePopupTrigger';
import { NewsletterSignup } from './NewsletterSignup';

interface NewsletterPopupProps {
  popup: PopupConfig;
}

export function NewsletterPopup({ popup }: NewsletterPopupProps) {
  const { isVisible, dismiss } = usePopupTrigger(popup);

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 p-4">
      <div className="relative w-full max-w-md overflow-hidden rounded-2xl bg-white shadow-2xl">
        <button
          onClick={dismiss}
          className="absolute right-3 top-3 z-10 rounded-full p-1.5 hover:bg-gray-100"
          type="button"
          aria-label="Close"
        >
          <X className="h-5 w-5 text-gray-500" />
        </button>

        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-center text-white">
          <Mail className="mx-auto mb-2 h-10 w-10" />
          <h3 className="text-xl font-bold">{popup.title}</h3>
          {popup.description && <p className="mt-1 text-sm text-blue-100">{popup.description}</p>}
        </div>

        <div className="p-6">
          <NewsletterSignup variant="inline" source="popup" />
          <button onClick={dismiss} className="mt-3 block w-full text-center text-sm text-gray-500 hover:text-gray-700" type="button">
            {popup.dismissLabel || 'No thanks'}
          </button>
        </div>
      </div>
    </div>
  );
}
