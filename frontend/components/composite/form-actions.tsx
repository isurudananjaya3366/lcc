import * as React from 'react';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

export interface FormActionsProps extends React.HTMLAttributes<HTMLDivElement> {
  submitLabel?: string;
  cancelLabel?: string;
  onCancel?: () => void;
  loading?: boolean;
  disabled?: boolean;
  align?: 'left' | 'center' | 'right';
}

function FormActions({
  submitLabel = 'Save',
  cancelLabel = 'Cancel',
  onCancel,
  loading = false,
  disabled = false,
  align = 'right',
  className,
  children,
  ...props
}: FormActionsProps) {
  return (
    <div
      className={cn(
        'flex gap-3 pt-4',
        align === 'left' && 'justify-start',
        align === 'center' && 'justify-center',
        align === 'right' && 'justify-end',
        className
      )}
      {...props}
    >
      {children ?? (
        <>
          {onCancel && (
            <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
              {cancelLabel}
            </Button>
          )}
          <Button type="submit" loading={loading} disabled={disabled}>
            {submitLabel}
          </Button>
        </>
      )}
    </div>
  );
}

export { FormActions };
