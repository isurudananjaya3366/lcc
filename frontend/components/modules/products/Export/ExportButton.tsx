'use client';

import { useState } from 'react';
import { Download, Loader2, FileText, FileSpreadsheet, FileDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';

export interface ExportFormat {
  id: 'csv' | 'excel' | 'pdf';
  label: string;
  description: string;
  icon: React.ReactNode;
  extension: string;
  mimeType: string;
}

const EXPORT_FORMATS: ExportFormat[] = [
  {
    id: 'csv',
    label: 'CSV',
    description: 'Comma-separated values',
    icon: <FileText className="h-5 w-5" />,
    extension: '.csv',
    mimeType: 'text/csv',
  },
  {
    id: 'excel',
    label: 'Excel',
    description: 'Microsoft Excel workbook',
    icon: <FileSpreadsheet className="h-5 w-5" />,
    extension: '.xlsx',
    mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  },
  {
    id: 'pdf',
    label: 'PDF',
    description: 'Printable product report',
    icon: <FileDown className="h-5 w-5" />,
    extension: '.pdf',
    mimeType: 'application/pdf',
  },
];

interface ExportButtonProps {
  selectedProducts?: string[];
  totalProducts: number;
  onExport: (format: ExportFormat) => void;
  isExporting?: boolean;
}

export function ExportButton({
  selectedProducts = [],
  totalProducts,
  onExport,
  isExporting,
}: ExportButtonProps) {
  const [open, setOpen] = useState(false);

  const handleFormatSelect = (format: ExportFormat) => {
    setOpen(false);
    onExport(format);
  };

  const scopeLabel =
    selectedProducts.length > 0 ? `${selectedProducts.length} selected` : `All ${totalProducts}`;

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" disabled={totalProducts === 0 || isExporting}>
          {isExporting ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Download className="mr-2 h-4 w-4" />
          )}
          Export
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-64 p-2" align="end">
        <div className="px-2 py-1.5 text-xs font-medium text-muted-foreground">
          Export {scopeLabel} products
        </div>
        <div className="space-y-1">
          {EXPORT_FORMATS.map((format) => (
            <button
              key={format.id}
              onClick={() => handleFormatSelect(format)}
              className="flex w-full items-center gap-3 rounded-md px-2 py-2 text-left hover:bg-accent transition-colors"
            >
              <span className="text-muted-foreground">{format.icon}</span>
              <div>
                <div className="text-sm font-medium">{format.label}</div>
                <div className="text-xs text-muted-foreground">{format.description}</div>
              </div>
            </button>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
}
