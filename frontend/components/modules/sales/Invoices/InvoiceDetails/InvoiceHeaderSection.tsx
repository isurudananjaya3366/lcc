'use client';

import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { InvoiceStatusBadge } from '../InvoiceStatusBadge';
import type { Invoice } from '@/services/api/invoiceService';

interface InvoiceHeaderSectionProps {
  invoice: Invoice;
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

export function InvoiceHeaderSection({ invoice }: InvoiceHeaderSectionProps) {
  const isOverdue = new Date(invoice.dueDate) < new Date() && invoice.balanceDue > 0;

  return (
    <div className="flex items-start justify-between">
      <div className="flex items-center gap-4">
        <Link href="/invoices">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold font-mono text-gray-900 dark:text-gray-100">
              {invoice.invoiceNumber}
            </h1>
            <InvoiceStatusBadge status={invoice.status} size="lg" />
          </div>
          <div className="mt-1 space-y-0.5 text-sm text-gray-500">
            <p>To: {invoice.customerName}</p>
            <p>
              Issued: {formatDate(invoice.issueDate)} · Due:{' '}
              <span className={isOverdue ? 'text-red-600 font-medium' : ''}>
                {formatDate(invoice.dueDate)}
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
