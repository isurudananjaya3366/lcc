import * as React from 'react';

import { cn } from '@/lib/utils';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

export interface AvatarGroupItem {
  id: string;
  name: string;
  image?: string;
}

export interface AvatarGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  avatars: AvatarGroupItem[];
  maxCount?: number;
  size?: 'sm' | 'md' | 'lg';
  onAvatarClick?: (avatar: AvatarGroupItem) => void;
}

const sizeClasses: Record<string, string> = {
  sm: 'h-8 w-8 text-xs',
  md: 'h-10 w-10 text-sm',
  lg: 'h-12 w-12 text-base',
};

const overlapClasses: Record<string, string> = {
  sm: '-ml-2',
  md: '-ml-3',
  lg: '-ml-4',
};

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

function AvatarGroup({
  avatars,
  maxCount = 3,
  size = 'md',
  onAvatarClick,
  className,
  ...props
}: AvatarGroupProps) {
  const visible = avatars.slice(0, maxCount);
  const remaining = avatars.length - maxCount;

  return (
    <div className={cn('flex items-center', className)} {...props}>
      {visible.map((avatar, index) => (
        <Avatar
          key={avatar.id}
          className={cn(
            sizeClasses[size],
            index > 0 && overlapClasses[size],
            'ring-2 ring-background transition-transform hover:z-10 hover:scale-110',
            onAvatarClick && 'cursor-pointer'
          )}
          onClick={() => onAvatarClick?.(avatar)}
          title={avatar.name}
        >
          {avatar.image && <AvatarImage src={avatar.image} alt={avatar.name} />}
          <AvatarFallback>{getInitials(avatar.name)}</AvatarFallback>
        </Avatar>
      ))}
      {remaining > 0 && (
        <div
          className={cn(
            sizeClasses[size],
            overlapClasses[size],
            'flex items-center justify-center rounded-full bg-muted font-medium text-muted-foreground ring-2 ring-background'
          )}
        >
          +{remaining}
        </div>
      )}
    </div>
  );
}

export { AvatarGroup };
