'use client';

import { cn } from '@/lib/cn';

interface UserAvatarProps {
  name?: string | null;
  email?: string | null;
  src?: string | null;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeMap = {
  sm: 'h-8 w-8 text-xs',
  md: 'h-10 w-10 text-sm',
  lg: 'h-12 w-12 text-base',
} as const;

export function UserAvatar({ name, email, src, size = 'md', className }: UserAvatarProps) {
  const initial = name?.[0]?.toUpperCase() ?? email?.[0]?.toUpperCase() ?? 'U';

  if (src) {
    return (
      <img
        src={src}
        alt={name ?? 'User avatar'}
        className={cn('rounded-full object-cover', sizeMap[size], className)}
      />
    );
  }

  return (
    <div
      className={cn(
        'flex items-center justify-center rounded-full bg-primary font-medium text-primary-foreground',
        sizeMap[size],
        className
      )}
      aria-hidden="true"
    >
      {initial}
    </div>
  );
}
