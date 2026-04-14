'use client';

import { ArrowRightLeft, Edit, Send, Printer, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { QuoteStatusBadge } from './QuoteStatusBadge';
import type { Quote, QuoteStatus } from '@/types/quotes';
import Link from 'next/link';

interface QuoteDetailsHeaderProps {
  quote: Quote;
  onConvert?: () => void;
  onSend?: () => void;
  onDelete?: () => void;
}

const editableStatuses: QuoteStatus[] = ['draft'];
const convertibleStatuses: QuoteStatus[] = ['sent', 'accepted'];
const sendableStatuses: QuoteStatus[] = ['draft', 'sent'];
const deletableStatuses: QuoteStatus[] = ['draft', 'sent', 'accepted', 'rejected', 'expired'];

export function QuoteDetailsHeader({
  quote,
  onConvert,
  onSend,
  onDelete,
}: QuoteDetailsHeaderProps) {
  const canEdit = editableStatuses.includes(quote.status);
  const canConvert = convertibleStatuses.includes(quote.status);
  const canSend = sendableStatuses.includes(quote.status);
  const canDelete = deletableStatuses.includes(quote.status);

  return (
    <div className="flex items-start justify-between">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold font-mono text-gray-900 dark:text-gray-100">
            {quote.quoteNumber}
          </h1>
          <QuoteStatusBadge status={quote.status} size="lg" />
        </div>
        <p className="mt-1 text-sm text-gray-500">
          {quote.customerName} ·{' '}
          {new Date(quote.quoteDate).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          })}
        </p>
      </div>

      <div className="flex items-center gap-2">
        {canEdit && (
          <Link href={`/quotes/${quote.id}?edit=true`}>
            <Button variant="outline" size="sm">
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </Button>
          </Link>
        )}
        {canSend && (
          <Button variant="outline" size="sm" onClick={onSend}>
            <Send className="mr-2 h-4 w-4" />
            {quote.status === 'sent' ? 'Resend' : 'Send'}
          </Button>
        )}
        {canConvert && (
          <Button size="sm" onClick={onConvert}>
            <ArrowRightLeft className="mr-2 h-4 w-4" />
            Convert to Order
          </Button>
        )}
        {quote.status === 'converted' && (
          <Button size="sm" disabled>
            <ArrowRightLeft className="mr-2 h-4 w-4" />
            Converted
          </Button>
        )}
        <Button variant="outline" size="sm" onClick={() => window.print()}>
          <Printer className="mr-2 h-4 w-4" />
          Print
        </Button>
        {canDelete && (
          <Button
            variant="outline"
            size="sm"
            className="text-red-600 hover:text-red-700"
            onClick={onDelete}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </Button>
        )}
      </div>
    </div>
  );
}
