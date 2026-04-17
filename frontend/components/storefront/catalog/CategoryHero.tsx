'use client';

import Image from 'next/image';
import { cn } from '@/lib/utils';

interface CategoryHeroProps {
  name: string;
  description?: string;
  image?: string;
  productCount?: number;
  className?: string;
}

export function CategoryHero({
  name,
  description,
  image,
  productCount,
  className,
}: CategoryHeroProps) {
  return (
    <section className={cn('relative w-full overflow-hidden rounded-xl', className)}>
      {/* Banner image or gradient fallback */}
      <div className="relative h-48 sm:h-56 md:h-64 lg:h-72 w-full">
        {image ? (
          <Image
            src={image}
            alt={`${name} category banner`}
            fill
            priority
            className="object-cover"
            sizes="(max-width: 768px) 100vw, 1200px"
          />
        ) : (
          <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700" />
        )}

        {/* Gradient overlay for text readability */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent" />

        {/* Content overlay */}
        <div className="absolute inset-0 flex flex-col justify-end p-6 sm:p-8 lg:p-10">
          <h1 className="text-3xl font-bold text-white sm:text-4xl lg:text-5xl">{name}</h1>

          <div className="mt-2 flex items-center gap-3">
            {productCount != null && (
              <span className="inline-flex items-center gap-1.5 text-sm text-white/80 sm:text-base">
                {/* Grid icon */}
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
                    d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z"
                  />
                </svg>
                {productCount} {productCount === 1 ? 'product' : 'products'}
              </span>
            )}
          </div>

          {description && (
            <p className="mt-2 max-w-2xl text-sm text-white/70 sm:text-base line-clamp-2">
              {description}
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
