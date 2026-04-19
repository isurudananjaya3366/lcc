'use client';

import Link from 'next/link';
import type { BannerAction } from '@/types/marketing/banner.types';

interface BannerCTAProps {
  cta: BannerAction;
  style?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  onClick?: () => void;
}

const styleClasses = {
  primary: 'bg-white text-gray-900 hover:bg-gray-100',
  secondary: 'bg-transparent border-2 border-white text-white hover:bg-white/10',
  ghost: 'text-white underline underline-offset-2 hover:opacity-80',
};

const sizeClasses = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-5 py-2.5 text-base',
  lg: 'px-7 py-3 text-lg',
};

export function BannerCTA({ cta, style = 'primary', size = 'md', className = '', onClick }: BannerCTAProps) {
  const cls = `inline-flex items-center justify-center rounded-full font-semibold transition-colors ${styleClasses[style]} ${sizeClasses[size]} ${className}`;

  if (cta.openInNewTab) {
    return (
      <a
        href={cta.url}
        target="_blank"
        rel="noopener noreferrer"
        className={cls}
        onClick={onClick}
      >
        {cta.label}
      </a>
    );
  }

  return (
    <Link href={cta.url} className={cls} onClick={onClick}>
      {cta.label}
    </Link>
  );
}
