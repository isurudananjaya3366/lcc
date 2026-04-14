'use client';

import { FileText, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

interface InvoicesHeaderProps {
  totalCount: number;
}

export function InvoicesHeader({ totalCount }: InvoicesHeaderProps) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-950">
          <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">Invoices</h2>
          <p className="text-sm text-gray-500">
            {totalCount} {totalCount === 1 ? 'invoice' : 'invoices'}
          </p>
        </div>
      </div>
      <Link href="/orders">
        <Button size="sm">
          <Plus className="mr-2 h-4 w-4" />
          Create from Order
        </Button>
      </Link>
    </div>
  );
}
