'use client';

import Link from 'next/link';
import { X } from 'lucide-react';
import { useAnnouncementStore } from '@/stores/store/announcement';
import type { Banner } from '@/types/marketing/banner.types';

interface TopBarBannerProps {
  banner: Banner;
  className?: string;
}

export function TopBarBanner({ banner, className = '' }: TopBarBannerProps) {
  const { dismiss, shouldShow } = useAnnouncementStore();

  if (!shouldShow()) return null;

  return (
    <div
      className={`relative flex items-center justify-center gap-2 px-4 py-2 text-center text-sm ${className}`}
      style={{
        backgroundColor: banner.backgroundColor || '#1e40af',
        color: banner.textColor || '#ffffff',
      }}
    >
      <span>{banner.title}</span>
      {banner.action && (
        <Link
          href={banner.action.url}
          className="font-semibold underline underline-offset-2 hover:opacity-80"
          target={banner.action.openInNewTab ? '_blank' : undefined}
        >
          {banner.action.label}
        </Link>
      )}
      {banner.isDismissible && (
        <button
          onClick={dismiss}
          className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-0.5 hover:bg-white/20"
          type="button"
          aria-label="Dismiss"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
