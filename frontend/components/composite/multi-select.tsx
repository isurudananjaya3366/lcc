'use client';

import * as React from 'react';
import { Check, X, ChevronsUpDown } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';

export interface MultiSelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface MultiSelectProps {
  options: MultiSelectOption[];
  value?: string[];
  onChange?: (value: string[]) => void;
  placeholder?: string;
  searchPlaceholder?: string;
  disabled?: boolean;
  maxSelected?: number;
  className?: string;
}

function MultiSelect({
  options,
  value = [],
  onChange,
  placeholder = 'Select items...',
  searchPlaceholder = 'Search...',
  disabled = false,
  maxSelected,
  className,
}: MultiSelectProps) {
  const [open, setOpen] = React.useState(false);
  const [search, setSearch] = React.useState('');
  const containerRef = React.useRef<HTMLDivElement>(null);

  const filtered = options.filter((opt) =>
    opt.label.toLowerCase().includes(search.toLowerCase())
  );

  const toggle = (optValue: string) => {
    const isSelected = value.includes(optValue);
    let next: string[];
    if (isSelected) {
      next = value.filter((v) => v !== optValue);
    } else {
      if (maxSelected && value.length >= maxSelected) return;
      next = [...value, optValue];
    }
    onChange?.(next);
  };

  const removeTag = (optValue: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onChange?.(value.filter((v) => v !== optValue));
  };

  // Close on outside click
  React.useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
        setSearch('');
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const selectedLabels = value
    .map((v) => options.find((o) => o.value === v))
    .filter(Boolean);

  return (
    <div ref={containerRef} className={cn('relative', className)}>
      <button
        type="button"
        onClick={() => !disabled && setOpen(!open)}
        disabled={disabled}
        className={cn(
          'flex min-h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background',
          'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
          disabled && 'cursor-not-allowed opacity-50'
        )}
        aria-expanded={open}
        aria-haspopup="listbox"
      >
        <div className="flex flex-1 flex-wrap gap-1">
          {selectedLabels.length > 0 ? (
            selectedLabels.map(
              (opt) =>
                opt && (
                  <Badge
                    key={opt.value}
                    variant="secondary"
                    className="gap-1 text-xs"
                  >
                    {opt.label}
                    <span
                      role="button"
                      tabIndex={0}
                      onClick={(e) => removeTag(opt.value, e)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          e.stopPropagation();
                          onChange?.(value.filter((v) => v !== opt.value));
                        }
                      }}
                      className="ml-0.5 rounded-full hover:bg-muted-foreground/20"
                      aria-label={`Remove ${opt.label}`}
                    >
                      <X className="h-3 w-3" />
                    </span>
                  </Badge>
                )
            )
          ) : (
            <span className="text-muted-foreground">{placeholder}</span>
          )}
        </div>
        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
      </button>

      {open && (
        <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover p-1 shadow-md animate-in fade-in-0 zoom-in-95">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={searchPlaceholder}
            className="mb-1 w-full rounded-sm border-0 bg-transparent px-2 py-1.5 text-sm outline-none placeholder:text-muted-foreground"
            aria-label="Search options"
          />
          <div className="max-h-60 overflow-auto" role="listbox">
            {filtered.length === 0 ? (
              <p className="px-2 py-4 text-center text-sm text-muted-foreground">
                No results found
              </p>
            ) : (
              filtered.map((opt) => {
                const selected = value.includes(opt.value);
                return (
                  <button
                    key={opt.value}
                    type="button"
                    role="option"
                    aria-selected={selected}
                    disabled={opt.disabled}
                    onClick={() => toggle(opt.value)}
                    className={cn(
                      'flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none',
                      'hover:bg-accent hover:text-accent-foreground',
                      opt.disabled && 'cursor-not-allowed opacity-50'
                    )}
                  >
                    <div
                      className={cn(
                        'flex h-4 w-4 shrink-0 items-center justify-center rounded-sm border',
                        selected
                          ? 'border-primary bg-primary text-primary-foreground'
                          : 'border-muted-foreground/50'
                      )}
                    >
                      {selected && <Check className="h-3 w-3" />}
                    </div>
                    {opt.label}
                  </button>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export { MultiSelect };
