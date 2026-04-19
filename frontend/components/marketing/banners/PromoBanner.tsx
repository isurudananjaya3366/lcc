'use client';

import Image from 'next/image';
import type { Banner } from '@/types/marketing/banner.types';
import { BannerCTA } from './BannerCTA';
import { trackBannerClick } from '@/lib/marketing/banner';

interface PromoBannerProps {
  banner: Banner;
  className?: string;
  onClick?: () => void;
}

export function PromoBanner({ banner, className = '', onClick }: PromoBannerProps) {
  const handleClick = () => {
    void trackBannerClick(banner.id);
    onClick?.();
  };

  return (
    <div
      className={`relative overflow-hidden rounded-xl ${className}`}
      style={{
        backgroundColor: banner.backgroundColor || '#1e40af',
        color: banner.textColor || '#ffffff',
      }}
    >
      {/* Background image */}
      {banner.imageUrl && (
        <Image
          src={banner.imageUrl}
          alt={banner.title}
          fill
          sizes="(max-width: 768px) 100vw, 50vw"
          className="object-cover opacity-20"
          priority={banner.priority === 1}
        />
      )}

      <div className="relative z-10 flex flex-col items-start gap-3 p-6">
        <h2 className="text-xl font-bold leading-tight">{banner.title}</h2>
        {banner.description && (
          <p className="text-sm opacity-90">{banner.description}</p>
        )}
        {banner.action && (
          <BannerCTA
            cta={banner.action}
            style="primary"
            onClick={handleClick}
          />
        )}
      </div>
    </div>
  );
}
