'use client';

import * as React from 'react';
import { Download, FileText, FileSpreadsheet, Table2, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

// ================================================================
// ExportButton — Dropdown for format selection + export trigger
// ================================================================

export type ExportFormat = 'PDF' | 'Excel' | 'CSV';

const formatConfig: Record<ExportFormat, { icon: React.ElementType; label: string }> = {
  PDF:   { icon: FileText,        label: 'PDF Document' },
  Excel: { icon: FileSpreadsheet, label: 'Excel Spreadsheet' },
  CSV:   { icon: Table2,          label: 'CSV File' },
};

export interface ExportButtonProps {
  onExport: (format: ExportFormat) => void;
  formats?: ExportFormat[];
  label?: string;
  disabled?: boolean;
  isLoading?: boolean;
  className?: string;
}

export function ExportButton({
  onExport,
  formats = ['PDF', 'Excel', 'CSV'],
  label = 'Export',
  disabled = false,
  isLoading = false,
  className,
}: ExportButtonProps) {
  const [open, setOpen] = React.useState(false);
  const containerRef = React.useRef<HTMLDivElement>(null);

  // Close on outside click
  React.useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [open]);

  // Close on Escape
  React.useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [open]);

  const handleSelect = (format: ExportFormat) => {
    setOpen(false);
    onExport(format);
  };

  return (
    <div ref={containerRef} className={cn('relative inline-block', className)}>
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        disabled={disabled || isLoading}
        className="inline-flex items-center gap-2 rounded-md border border-input bg-background px-3 py-2 text-sm font-medium text-foreground transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
        aria-expanded={open}
        aria-haspopup="listbox"
      >
        {isLoading ? (
          <Loader2 className="size-4 animate-spin" />
        ) : (
          <Download className="size-4" />
        )}
        {isLoading ? 'Exporting…' : label}
      </button>

      {open && (
        <div
          role="listbox"
          className="absolute right-0 z-50 mt-1 min-w-[180px] rounded-md border bg-popover p-1 shadow-md animate-in fade-in-0 zoom-in-95"
        >
          {formats.map((format) => {
            const config = formatConfig[format];
            const FormatIcon = config.icon;
            return (
              <button
                key={format}
                type="button"
                role="option"
                aria-selected={false}
                onClick={() => handleSelect(format)}
                className="flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm text-foreground hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:bg-accent"
              >
                <FormatIcon className="size-4 text-muted-foreground" />
                {config.label}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
