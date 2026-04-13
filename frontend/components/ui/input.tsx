import * as React from 'react';

import { cn } from '@/lib/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  prefixIcon?: React.ReactNode;
  suffixIcon?: React.ReactNode;
  clearable?: boolean;
  onClear?: () => void;
  validation?: 'default' | 'success' | 'warning' | 'error';
  helperText?: string;
  addonBefore?: React.ReactNode;
  addonAfter?: React.ReactNode;
  inputSize?: 'sm' | 'default' | 'lg';
  showCount?: boolean;
}

const validationStyles: Record<string, string> = {
  default: 'border-input focus-visible:ring-ring',
  success: 'border-success-500 focus-visible:ring-success-500',
  warning: 'border-warning-500 focus-visible:ring-warning-500',
  error: 'border-error-500 focus-visible:ring-error-500',
};

const helperTextStyles: Record<string, string> = {
  default: 'text-muted-foreground',
  success: 'text-success-600',
  warning: 'text-warning-600',
  error: 'text-error-600',
};

const sizeStyles: Record<string, string> = {
  sm: 'h-8 text-xs px-2.5 py-1',
  default: 'h-10 text-sm px-3 py-2',
  lg: 'h-12 text-base px-4 py-3',
};

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      type,
      prefixIcon,
      suffixIcon,
      clearable,
      onClear,
      validation = 'default',
      helperText,
      addonBefore,
      addonAfter,
      inputSize = 'default',
      showCount,
      maxLength,
      value,
      ...props
    },
    ref
  ) => {
    const hasAddons = addonBefore || addonAfter;
    const hasIcons = prefixIcon || suffixIcon || clearable;

    const inputElement = (
      <div className={cn('relative', hasIcons && 'flex items-center')}>
        {prefixIcon && (
          <span className="pointer-events-none absolute left-3 flex items-center text-muted-foreground">
            {prefixIcon}
          </span>
        )}
        <input
          type={type}
          className={cn(
            'flex w-full rounded-md border bg-background ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
            sizeStyles[inputSize],
            validationStyles[validation],
            prefixIcon && 'pl-10',
            (suffixIcon || clearable) && 'pr-10',
            hasAddons && addonBefore && 'rounded-l-none',
            hasAddons && addonAfter && 'rounded-r-none',
            className
          )}
          ref={ref}
          value={value}
          {...props}
        />
        {(suffixIcon || (clearable && value)) && (
          <span className="absolute right-3 flex items-center">
            {clearable && value ? (
              <button
                type="button"
                onClick={onClear}
                className="text-muted-foreground hover:text-foreground"
                aria-label="Clear input"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            ) : (
              <span className="pointer-events-none text-muted-foreground">{suffixIcon}</span>
            )}
          </span>
        )}
      </div>
    );

    const wrappedInput = hasAddons ? (
      <div className="flex">
        {addonBefore && (
          <span className="inline-flex items-center rounded-l-md border border-r-0 border-input bg-muted px-3 text-sm text-muted-foreground">
            {addonBefore}
          </span>
        )}
        {inputElement}
        {addonAfter && (
          <span className="inline-flex items-center rounded-r-md border border-l-0 border-input bg-muted px-3 text-sm text-muted-foreground">
            {addonAfter}
          </span>
        )}
      </div>
    ) : (
      inputElement
    );

    if (helperText || (showCount && maxLength)) {
      return (
        <div>
          {wrappedInput}
          <div className="mt-1 flex items-center justify-between gap-2">
            {helperText && (
              <p className={cn('text-xs', helperTextStyles[validation])}>{helperText}</p>
            )}
            {showCount && maxLength && (
              <span className="ml-auto text-xs text-muted-foreground">
                {String(value ?? '').length}/{maxLength}
              </span>
            )}
          </div>
        </div>
      );
    }

    return wrappedInput;
  }
);
Input.displayName = 'Input';

export { Input };
