'use client';

import * as React from 'react';

import { cn } from '@/lib/utils';

export interface ButtonGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: 'horizontal' | 'vertical';
  spacing?: 'attached' | 'detached';
}

const ButtonGroup = React.forwardRef<HTMLDivElement, ButtonGroupProps>(
  ({ className, orientation = 'horizontal', spacing = 'attached', children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        role="group"
        className={cn(
          'inline-flex',
          orientation === 'vertical' ? 'flex-col' : 'flex-row',
          spacing === 'attached'
            ? orientation === 'horizontal'
              ? '[&>*:not(:first-child)]:rounded-l-none [&>*:not(:last-child)]:rounded-r-none [&>*:not(:first-child)]:-ml-px'
              : '[&>*:not(:first-child)]:rounded-t-none [&>*:not(:last-child)]:rounded-b-none [&>*:not(:first-child)]:-mt-px'
            : 'gap-1',
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);
ButtonGroup.displayName = 'ButtonGroup';

// --- ToggleButtonGroup ---
export interface ToggleButtonGroupProps<T extends string = string> {
  options: { value: T; label: React.ReactNode }[];
  value?: T | T[];
  onChange?: (value: T | T[]) => void;
  multiple?: boolean;
  size?: 'sm' | 'default' | 'lg';
  className?: string;
}

export function ToggleButtonGroup<T extends string = string>({
  options,
  value,
  onChange,
  multiple = false,
  size = 'default',
  className,
}: ToggleButtonGroupProps<T>) {
  const selected = Array.isArray(value) ? value : value ? [value] : [];

  const sizeClasses = {
    sm: 'h-8 px-3 text-xs',
    default: 'h-10 px-4 text-sm',
    lg: 'h-12 px-6 text-base',
  };

  const handleClick = (optionValue: T) => {
    if (multiple) {
      const next = selected.includes(optionValue)
        ? selected.filter((v) => v !== optionValue)
        : [...selected, optionValue];
      onChange?.(next);
    } else {
      onChange?.(optionValue);
    }
  };

  return (
    <div role="group" className={cn('inline-flex rounded-md border border-input', className)}>
      {options.map((option, index) => {
        const isSelected = selected.includes(option.value);
        return (
          <button
            key={option.value}
            type="button"
            role={multiple ? 'checkbox' : 'radio'}
            aria-checked={isSelected}
            onClick={() => handleClick(option.value)}
            className={cn(
              'inline-flex items-center justify-center font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
              sizeClasses[size],
              isSelected
                ? 'bg-primary text-primary-foreground'
                : 'bg-background text-foreground hover:bg-accent',
              index > 0 && 'border-l border-input',
              index === 0 && 'rounded-l-md',
              index === options.length - 1 && 'rounded-r-md',
            )}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}

export { ButtonGroup };
