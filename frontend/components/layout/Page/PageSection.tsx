'use client';

import { useState, type ReactNode } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/cn';

interface PageSectionProps {
  title?: string;
  description?: string;
  children: ReactNode;
  actions?: ReactNode;
  collapsible?: boolean;
  defaultExpanded?: boolean;
  className?: string;
}

export function PageSection({
  title,
  description,
  children,
  actions,
  collapsible = false,
  defaultExpanded = true,
  className,
}: PageSectionProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const header = title ? (
    <div className="flex items-start justify-between gap-4">
      <div>
        {collapsible ? (
          <button
            type="button"
            onClick={() => setIsExpanded((prev) => !prev)}
            className="flex items-center gap-2 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            aria-expanded={isExpanded}
          >
            <h2 className="text-xl font-semibold text-foreground">{title}</h2>
            <ChevronDown
              className={cn(
                'h-5 w-5 text-muted-foreground transition-transform duration-200',
                isExpanded && 'rotate-180'
              )}
            />
          </button>
        ) : (
          <h2 className="text-xl font-semibold text-foreground">{title}</h2>
        )}
        {description && <p className="mt-1 text-sm text-muted-foreground">{description}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  ) : null;

  return (
    <section className={cn('border-b py-6 first:pt-0 last:border-b-0 md:py-8', className)}>
      {header}
      {collapsible ? (
        <div
          className={cn(
            'overflow-hidden transition-[max-height,opacity] duration-300',
            isExpanded ? 'mt-4 max-h-[2000px] opacity-100' : 'max-h-0 opacity-0'
          )}
        >
          {children}
        </div>
      ) : (
        <div className={title ? 'mt-4' : undefined}>{children}</div>
      )}
    </section>
  );
}
