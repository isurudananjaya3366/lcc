import * as React from 'react';

import { cn } from '@/lib/utils';

export interface FormSectionProps extends React.HTMLAttributes<HTMLElement> {
  title?: string;
  description?: string;
  collapsible?: boolean;
  defaultCollapsed?: boolean;
}

function FormSection({
  title,
  description,
  collapsible = false,
  defaultCollapsed = false,
  className,
  children,
  ...props
}: FormSectionProps) {
  const [collapsed, setCollapsed] = React.useState(defaultCollapsed);

  return (
    <fieldset className={cn('space-y-4', className)} {...props}>
      {(title || description) && (
        <div className="space-y-1">
          {title && (
            <legend
              className={cn(
                'text-base font-semibold leading-7 text-foreground',
                collapsible && 'cursor-pointer select-none'
              )}
              onClick={collapsible ? () => setCollapsed(!collapsed) : undefined}
            >
              {title}
              {collapsible && (
                <span className="ml-2 text-sm text-muted-foreground">
                  {collapsed ? '▸' : '▾'}
                </span>
              )}
            </legend>
          )}
          {description && (
            <p className="text-sm text-muted-foreground">{description}</p>
          )}
        </div>
      )}
      {(!collapsible || !collapsed) && (
        <div className="space-y-4">{children}</div>
      )}
    </fieldset>
  );
}

export { FormSection };
