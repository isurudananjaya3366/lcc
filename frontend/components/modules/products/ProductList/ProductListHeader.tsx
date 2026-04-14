import Link from 'next/link';
import { Plus } from 'lucide-react';
import { ExportButton } from '../Export';
import type { ExportFormat } from '../Export';
import { ImportButton } from '../Import';

interface ProductListHeaderProps {
  title?: string;
  description?: string;
  totalProducts?: number;
  onExport?: (format: ExportFormat) => void;
  onImport?: () => void;
}

export function ProductListHeader({
  title = 'Products',
  description = 'Manage your product catalog',
  totalProducts = 0,
  onExport,
  onImport,
}: ProductListHeaderProps) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 sm:text-3xl">{title}</h1>
        {description && (
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{description}</p>
        )}
      </div>
      <div className="flex items-center gap-2">
        {onExport && (
          <ExportButton totalProducts={totalProducts} onExport={onExport} />
        )}
        {onImport && (
          <ImportButton onImport={onImport} />
        )}
        <Link
          href="/products/new"
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          <Plus className="h-4 w-4" />
          Create Product
        </Link>
      </div>
    </div>
  );
}
