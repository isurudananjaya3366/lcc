import Link from 'next/link';

import { cn } from '@/lib/cn';

export interface AuthLogoProps {
  size?: 'sm' | 'md' | 'lg';
  withLink?: boolean;
  className?: string;
}

const sizeMap = {
  sm: 'text-xl',
  md: 'text-2xl',
  lg: 'text-3xl',
} as const;

const subtitleSizeMap = {
  sm: 'text-xs',
  md: 'text-sm',
  lg: 'text-base',
} as const;

export function AuthLogo({ size = 'md', withLink = true, className }: AuthLogoProps) {
  const content = (
    <div className={cn('text-center', className)}>
      <h1 className={cn('font-bold text-gray-900 dark:text-gray-100', sizeMap[size])}>
        LankaCommerce Cloud
      </h1>
      <p className={cn('mt-1 text-gray-500 dark:text-gray-400', subtitleSizeMap[size])}>
        Multi-tenant ERP for Sri Lankan SMEs
      </p>
    </div>
  );

  if (withLink) {
    return (
      <Link href="/" className="inline-block" aria-label="Go to LankaCommerce Cloud homepage">
        {content}
      </Link>
    );
  }

  return content;
}
