'use client';

import { FileText, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

interface QuotesHeaderProps {
  totalCount: number;
}

export function QuotesHeader({ totalCount }: QuotesHeaderProps) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-50 dark:bg-purple-950">
          <FileText className="h-5 w-5 text-purple-600 dark:text-purple-400" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">Quotes</h2>
          <p className="text-sm text-gray-500">
            {totalCount} {totalCount === 1 ? 'quote' : 'quotes'}
          </p>
        </div>
      </div>
      <Link href="/quotes/new">
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Quote
        </Button>
      </Link>
    </div>
  );
}
