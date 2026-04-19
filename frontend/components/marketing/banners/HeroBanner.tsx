'use client';

import { useState, useEffect, useCallback } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useHeroBanners } from '@/hooks/marketing/useBanners';
import { trackBannerClick } from '@/lib/marketing/banner';

export function HeroBanner({ className = '' }: { className?: string }) {
  const { data: banners } = useHeroBanners();
  const [current, setCurrent] = useState(0);

  const next = useCallback(() => {
    if (banners) setCurrent((c) => (c + 1) % banners.length);
  }, [banners]);

  const prev = useCallback(() => {
    if (banners) setCurrent((c) => (c - 1 + banners.length) % banners.length);
  }, [banners]);

  useEffect(() => {
    if (!banners || banners.length <= 1) return;
    const interval = setInterval(next, 5000);
    return () => clearInterval(interval);
  }, [banners, next]);

  if (!banners?.length) return null;

  const banner = banners[current];

  const content = (
    <div
      className={`relative h-[300px] overflow-hidden rounded-xl md:h-[400px] lg:h-[500px] ${className}`}
      style={{ backgroundColor: banner.backgroundColor || '#f3f4f6' }}
    >
      {banner.imageUrl && (
        <Image
          src={banner.imageUrl}
          alt={banner.title}
          fill
          sizes="100vw"
          className="object-cover"
          priority={current === 0}
        />
      )}

      <div className="absolute inset-0 bg-gradient-to-r from-black/40 to-transparent" />

      <div className="absolute bottom-0 left-0 p-6 md:p-10">
        <h2 className="text-2xl font-bold text-white md:text-4xl" style={{ color: banner.textColor || 'white' }}>
          {banner.title}
        </h2>
        {banner.description && (
          <p className="mt-2 max-w-lg text-sm text-white/90 md:text-base">{banner.description}</p>
        )}
        {banner.action && (
          <span className="mt-4 inline-block rounded-lg bg-white px-6 py-2.5 text-sm font-semibold text-gray-900 transition-colors hover:bg-gray-100">
            {banner.action.label}
          </span>
        )}
      </div>

      {banners.length > 1 && (
        <>
          <button
            onClick={(e) => { e.preventDefault(); prev(); }}
            className="absolute left-3 top-1/2 -translate-y-1/2 rounded-full bg-white/80 p-2 shadow hover:bg-white"
            type="button"
            aria-label="Previous slide"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <button
            onClick={(e) => { e.preventDefault(); next(); }}
            className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full bg-white/80 p-2 shadow hover:bg-white"
            type="button"
            aria-label="Next slide"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
          <div className="absolute bottom-3 left-1/2 flex -translate-x-1/2 gap-1.5">
            {banners.map((_, i) => (
              <button
                key={i}
                onClick={(e) => { e.preventDefault(); setCurrent(i); }}
                className={`h-2 rounded-full transition-all ${i === current ? 'w-6 bg-white' : 'w-2 bg-white/50'}`}
                type="button"
                aria-label={`Go to slide ${i + 1}`}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );

  if (banner.action?.url) {
    return (
      <Link
        href={banner.action.url}
        target={banner.action.openInNewTab ? '_blank' : undefined}
        rel={banner.action.openInNewTab ? 'noopener noreferrer' : undefined}
        onClick={() => trackBannerClick(banner.id)}
      >
        {content}
      </Link>
    );
  }

  return content;
}
