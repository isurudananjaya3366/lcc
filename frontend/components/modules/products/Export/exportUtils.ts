import type { ExportFormat } from './ExportButton';

/**
 * Export column configuration for product data
 */
const EXPORT_COLUMNS = [
  { key: 'name', label: 'Name' },
  { key: 'sku', label: 'SKU' },
  { key: 'description', label: 'Description' },
  { key: 'pricing.cost', label: 'Cost Price' },
  { key: 'pricing.basePrice', label: 'Selling Price' },
  { key: 'inventory.stockQuantity', label: 'Stock Quantity' },
  { key: 'status', label: 'Status' },
  { key: 'createdAt', label: 'Created Date' },
] as const;

interface ExportableProduct {
  name: string;
  sku: string;
  description?: string;
  pricing?: { cost?: number; basePrice?: number };
  inventory?: { stockQuantity?: number };
  status: string;
  createdAt?: string;
}

function getNestedValue(obj: Record<string, unknown>, path: string): unknown {
  return path.split('.').reduce((acc: unknown, key) => {
    if (acc && typeof acc === 'object') return (acc as Record<string, unknown>)[key];
    return undefined;
  }, obj);
}

/**
 * Download a blob as a file
 */
function downloadFile(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Generate and download CSV client-side
 */
export function exportToCSV(products: ExportableProduct[], filename = 'products') {
  const headers = EXPORT_COLUMNS.map((c) => c.label);
  const rows = products.map((product) =>
    EXPORT_COLUMNS.map((col) => {
      const value = getNestedValue(product as unknown as Record<string, unknown>, col.key);
      if (value === null || value === undefined) return '';
      return String(value);
    })
  );

  const csvContent = [
    headers.join(','),
    ...rows.map((row) =>
      row
        .map((cell) => {
          // Escape cells containing commas, quotes, or newlines
          if (/[,"\n\r]/.test(cell)) {
            return `"${cell.replace(/"/g, '""')}"`;
          }
          return cell;
        })
        .join(',')
    ),
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  downloadFile(blob, `${filename}.csv`);
}

/**
 * Request Excel export from server
 */
export async function exportToExcel(filters?: Record<string, unknown>, productIds?: string[]) {
  // TODO: Replace with actual API call
  const response = await fetch('/api/v1/products/export/excel', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filters, productIds }),
  });

  if (!response.ok) throw new Error('Export failed');

  const blob = await response.blob();
  const disposition = response.headers.get('Content-Disposition');
  const filename = disposition?.match(/filename="?(.+?)"?$/)?.[1] || 'products.xlsx';
  downloadFile(blob, filename);
}

/**
 * Request PDF export from server
 */
export async function exportToPDF(filters?: Record<string, unknown>, productIds?: string[]) {
  // TODO: Replace with actual API call
  const response = await fetch('/api/v1/products/export/pdf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filters, productIds }),
  });

  if (!response.ok) throw new Error('Export failed');

  const blob = await response.blob();
  const disposition = response.headers.get('Content-Disposition');
  const filename = disposition?.match(/filename="?(.+?)"?$/)?.[1] || 'products.pdf';
  downloadFile(blob, filename);
}

/**
 * Handle export based on selected format
 */
export async function handleExport(
  format: ExportFormat,
  products: ExportableProduct[],
  filters?: Record<string, unknown>,
  productIds?: string[]
) {
  switch (format.id) {
    case 'csv':
      exportToCSV(products);
      break;
    case 'excel':
      await exportToExcel(filters, productIds);
      break;
    case 'pdf':
      await exportToPDF(filters, productIds);
      break;
  }
}
