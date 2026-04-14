'use client';

import { FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

interface InvoiceSummaryCardsProps {
  totalInvoices: number;
  paidTotal: number;
  outstandingTotal: number;
}

function formatCurrency(amount: number): string {
  return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

export function InvoiceSummaryCards({
  totalInvoices,
  paidTotal,
  outstandingTotal,
}: InvoiceSummaryCardsProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <Card>
        <CardContent className="flex items-center gap-4 pt-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-950">
            <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <p className="text-sm text-gray-500">Total Invoices</p>
            <p className="text-2xl font-bold">{totalInvoices}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="flex items-center gap-4 pt-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-50 dark:bg-green-950">
            <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400" />
          </div>
          <div>
            <p className="text-sm text-gray-500">Paid</p>
            <p className="text-2xl font-bold text-green-600">{formatCurrency(paidTotal)}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="flex items-center gap-4 pt-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-orange-50 dark:bg-orange-950">
            <AlertCircle className="h-5 w-5 text-orange-600 dark:text-orange-400" />
          </div>
          <div>
            <p className="text-sm text-gray-500">Outstanding</p>
            <p className="text-2xl font-bold text-orange-600">{formatCurrency(outstandingTotal)}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
