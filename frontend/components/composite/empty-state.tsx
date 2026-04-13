import * as React from 'react';
import { type LucideIcon } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

export interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  size?: 'sm' | 'default' | 'lg';
  className?: string;
}

const sizeConfig = {
  sm: { icon: 'h-8 w-8', title: 'text-sm', desc: 'text-xs', gap: 'gap-2', py: 'py-6' },
  default: { icon: 'h-12 w-12', title: 'text-lg', desc: 'text-sm', gap: 'gap-3', py: 'py-12' },
  lg: { icon: 'h-16 w-16', title: 'text-xl', desc: 'text-base', gap: 'gap-4', py: 'py-16' },
} as const;

function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  size = 'default',
  className,
}: EmptyStateProps) {
  const config = sizeConfig[size];

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center text-center',
        config.gap,
        config.py,
        className
      )}
    >
      {Icon && (
        <div className="rounded-full bg-muted p-4">
          <Icon className={cn(config.icon, 'text-muted-foreground')} />
        </div>
      )}
      <div className="space-y-1">
        <h3 className={cn('font-semibold', config.title)}>{title}</h3>
        {description && (
          <p className={cn('text-muted-foreground', config.desc)}>
            {description}
          </p>
        )}
      </div>
      {action && (
        <Button onClick={action.onClick} size={size === 'sm' ? 'sm' : 'default'}>
          {action.label}
        </Button>
      )}
    </div>
  );
}

export { EmptyState };
