'use client';

import { X, Gift } from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import type { PopupConfig } from '@/types/marketing/popup.types';
import { usePopupTrigger } from '@/hooks/marketing/usePopupTrigger';

interface PromotionalPopupProps {
  popup: PopupConfig;
  className?: string;
}

export function PromotionalPopup({ popup, className = '' }: PromotionalPopupProps) {
  const { isVisible, dismiss } = usePopupTrigger(popup);

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 p-4">
      <div className={`relative w-full max-w-md overflow-hidden rounded-2xl bg-white shadow-2xl ${className}`}>
        <button
          onClick={dismiss}
          className="absolute right-3 top-3 z-10 rounded-full bg-white/80 p-1.5 shadow hover:bg-white"
          type="button"
          aria-label="Close"
        >
          <X className="h-5 w-5 text-gray-600" />
        </button>

        {popup.imageUrl && (
          <div className="relative h-48 w-full">
            <Image src={popup.imageUrl} alt={popup.title} fill className="object-cover" />
          </div>
        )}

        <div className="p-6 text-center">
          <Gift className="mx-auto mb-3 h-8 w-8 text-blue-600" />
          <h3 className="text-xl font-bold text-gray-900">{popup.title}</h3>
          {popup.description && <p className="mt-2 text-sm text-gray-600">{popup.description}</p>}

          <div className="mt-5 flex flex-col gap-2">
            {popup.action && (
              <Link
                href={popup.action.url || '#'}
                onClick={dismiss}
                className="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
              >
                {popup.action.label}
              </Link>
            )}
            <button onClick={dismiss} className="text-sm text-gray-500 hover:text-gray-700" type="button">
              {popup.dismissLabel || 'No thanks'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
