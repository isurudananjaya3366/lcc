'use client';

import { createColumnHelper } from '@tanstack/react-table';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Eye, Edit, ArrowRightLeft, Trash2, MoreVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { QuoteStatusBadge } from './QuoteStatusBadge';
import type { Quote } from '@/types/quotes';

function formatCurrency(amount: number): string {
  return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

const columnHelper = createColumnHelper<Quote>();

export interface QuoteColumnCallbacks {
  onConvert?: (quote: Quote) => void;
  onDelete?: (quote: Quote) => void;
}

function QuoteActionsCell({
  quote,
  callbacks,
}: {
  quote: Quote;
  callbacks?: QuoteColumnCallbacks;
}) {
  const router = useRouter();
  const canEdit = ['draft'].includes(quote.status);
  const canConvert = ['sent', 'accepted'].includes(quote.status);
  const canDelete = !['converted'].includes(quote.status);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <MoreVertical className="h-4 w-4" />
          <span className="sr-only">Quote actions</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[160px]">
        <DropdownMenuItem onClick={() => router.push(`/quotes/${quote.id}`)}>
          <Eye className="mr-2 h-4 w-4" />
          View
        </DropdownMenuItem>
        {canEdit && (
          <DropdownMenuItem onClick={() => router.push(`/quotes/${quote.id}?edit=true`)}>
            <Edit className="mr-2 h-4 w-4" />
            Edit
          </DropdownMenuItem>
        )}
        {canConvert && (
          <DropdownMenuItem onClick={() => callbacks?.onConvert?.(quote)}>
            <ArrowRightLeft className="mr-2 h-4 w-4" />
            Convert to Order
          </DropdownMenuItem>
        )}
        {canDelete && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => callbacks?.onDelete?.(quote)}
              className="text-red-600 dark:text-red-400"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export function getQuoteColumns(callbacks?: QuoteColumnCallbacks) {
  return [
    columnHelper.accessor('quoteNumber', {
      header: 'Quote #',
      size: 120,
      cell: (info) => (
        <Link
          href={`/quotes/${info.row.original.id}`}
          className="font-medium text-blue-600 hover:underline dark:text-blue-400"
        >
          {info.getValue()}
        </Link>
      ),
    }),
    columnHelper.accessor('customerName', {
      header: 'Customer',
      size: 200,
      cell: (info) => (
        <span className="truncate block max-w-[200px]">{info.getValue()}</span>
      ),
    }),
    columnHelper.accessor('quoteDate', {
      header: 'Date',
      size: 120,
      cell: (info) => formatDate(info.getValue()),
    }),
    columnHelper.accessor('expiryDate', {
      header: 'Expiry',
      size: 120,
      cell: (info) => {
        const expiry = new Date(info.getValue());
        const isExpired = expiry < new Date() && info.row.original.status !== 'converted';
        return (
          <span className={isExpired ? 'text-red-600 font-medium' : ''}>
            {formatDate(info.getValue())}
          </span>
        );
      },
    }),
    columnHelper.accessor('total', {
      header: () => <span className="text-right block">Amount (LKR)</span>,
      size: 120,
      cell: (info) => (
        <span className="text-right block font-medium">
          {formatCurrency(info.getValue())}
        </span>
      ),
    }),
    columnHelper.accessor('status', {
      header: 'Status',
      size: 100,
      cell: (info) => <QuoteStatusBadge status={info.getValue()} />,
    }),
    columnHelper.display({
      id: 'actions',
      size: 80,
      cell: (info) => (
        <QuoteActionsCell
          quote={info.row.original}
          callbacks={callbacks}
        />
      ),
    }),
  ];
}
