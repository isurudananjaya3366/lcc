import Image from 'next/image';
import Link from 'next/link';
import { cn } from '@/lib/utils';

interface CollectionBannerProps {
  title: string;
  subtitle?: string;
  image?: string;
  href: string;
  ctaText?: string;
  className?: string;
}

export function CollectionBanner({
  title,
  subtitle,
  image,
  href,
  ctaText = 'Shop Now',
  className,
}: CollectionBannerProps) {
  return (
    <Link
      href={href}
      className={cn('group relative block w-full overflow-hidden rounded-xl', className)}
    >
      <div className="relative h-40 sm:h-48 lg:h-56 w-full">
        {image ? (
          <Image
            src={image}
            alt={title}
            fill
            className="object-cover transition-transform duration-500 group-hover:scale-105"
            sizes="(max-width: 768px) 100vw, 1200px"
          />
        ) : (
          <div className="absolute inset-0 bg-gradient-to-r from-indigo-600 to-purple-600" />
        )}

        {/* Overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-black/60 via-black/30 to-transparent" />

        {/* Content */}
        <div className="absolute inset-0 flex flex-col justify-center px-6 sm:px-10 lg:px-14">
          <h3 className="text-xl font-bold text-white sm:text-2xl lg:text-3xl">{title}</h3>
          {subtitle && (
            <p className="mt-1.5 max-w-md text-sm text-white/80 sm:text-base">{subtitle}</p>
          )}
          <span className="mt-3 inline-flex w-fit items-center gap-1.5 rounded-lg bg-white px-4 py-2 text-sm font-medium text-gray-900 transition-colors group-hover:bg-gray-100">
            {ctaText}
            {/* Arrow right icon */}
            <svg
              className="h-4 w-4 transition-transform group-hover:translate-x-0.5"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"
              />
            </svg>
          </span>
        </div>
      </div>
    </Link>
  );
}
