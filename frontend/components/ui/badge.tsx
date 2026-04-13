import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';

import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary text-primary-foreground hover:bg-primary/80',
        secondary: 'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
        destructive: 'border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80',
        outline: 'text-foreground',
        // Status variants
        pending: 'border-transparent bg-warning-100 text-warning-800 dark:bg-warning-900 dark:text-warning-100',
        confirmed: 'border-transparent bg-info-100 text-info-800 dark:bg-info-900 dark:text-info-100',
        processing: 'border-transparent bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-100',
        shipped: 'border-transparent bg-info-100 text-info-800 dark:bg-info-900 dark:text-info-100',
        delivered: 'border-transparent bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-100',
        cancelled: 'border-transparent bg-secondary-100 text-secondary-800 dark:bg-secondary-900 dark:text-secondary-100',
        failed: 'border-transparent bg-error-100 text-error-800 dark:bg-error-900 dark:text-error-100',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
