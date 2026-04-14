import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';

interface PageTitleProps {
  title: string;
  description?: string | ReactNode;
  actions?: ReactNode;
  className?: string;
}

export function PageTitle({ title, description, actions, className }: PageTitleProps) {
  return (
    <div
      className={cn('flex flex-col justify-between gap-4 md:flex-row md:items-start', className)}
    >
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground md:text-4xl">{title}</h1>
        {description && (
          <div className="mt-2 text-base text-muted-foreground md:text-lg">
            {typeof description === 'string' ? <p>{description}</p> : description}
          </div>
        )}
      </div>
      {actions}
    </div>
  );
}
