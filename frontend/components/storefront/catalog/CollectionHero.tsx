'use client';

import Image from 'next/image';
import { cn } from '@/lib/utils';

interface CollectionHeroProps {
  name: string;
  description?: string;
  image?: string;
  productCount?: number;
  curatedBy?: string | null;
  tags?: string[];
  className?: string;
}

export function CollectionHero({
  name,
  description,
  image,
  productCount,
  curatedBy,
  tags,
  className,
}: CollectionHeroProps) {
  return (
    <section className={cn('relative w-full overflow-hidden rounded-xl', className)}>
      {/* Hero image or gradient fallback */}
      <div className="relative h-64 sm:h-80 md:h-96 lg:h-[28rem] w-full">
        {image ? (
          <Image
            src={image}
            alt={`${name} collection`}
            fill
            priority
            className="object-cover"
            sizes="(max-width: 768px) 100vw, 1200px"
          />
        ) : (
          <div className="absolute inset-0 bg-gradient-to-br from-rose-500 via-fuchsia-600 to-indigo-700" />
        )}

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />

        {/* Content */}
        <div className="absolute inset-0 flex flex-col justify-end p-6 sm:p-8 lg:p-12">
          {/* Tags */}
          {tags && tags.length > 0 && (
            <div className="mb-3 flex flex-wrap gap-2">
              {tags.map((tag) => (
                <span
                  key={tag}
                  className="rounded-full bg-white/20 px-3 py-0.5 text-xs font-medium text-white backdrop-blur-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}

          <h1 className="text-3xl font-bold text-white sm:text-4xl md:text-5xl lg:text-6xl">
            {name}
          </h1>

          {/* Metadata row */}
          <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-white/80 sm:text-base">
            {curatedBy && (
              <span className="inline-flex items-center gap-1.5">
                {/* User icon */}
                <svg
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z"
                  />
                </svg>
                Curated by {curatedBy}
              </span>
            )}

            {productCount != null && (
              <span className="inline-flex items-center gap-1.5">
                {/* Package icon */}
                <svg
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="m21 7.5-9-5.25L3 7.5m18 0-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9"
                  />
                </svg>
                {productCount} handpicked {productCount === 1 ? 'product' : 'products'}
              </span>
            )}
          </div>

          {description && (
            <p className="mt-3 max-w-2xl text-sm text-white/70 sm:text-base lg:text-lg line-clamp-2">
              {description}
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
