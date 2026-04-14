'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { salesKeys } from '@/lib/queryKeys';
import { invoiceService } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Send, CreditCard } from 'lucide-react';
import Link from 'next/link';
import {
  InvoiceHeaderSection,
  InvoicePDFPreview,
  DownloadPDFButton,
  PrintInvoiceButton,
  SendInvoiceModal,
  PaymentHistory,
} from './InvoiceDetails';

interface InvoiceDetailProps {
  invoiceId: string;
}

function formatCurrency(amount: number): string {
  return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

export function InvoiceDetail({ invoiceId }: InvoiceDetailProps) {
  const [sendModalOpen, setSendModalOpen] = useState(false);

  const {
    data: invoice,
    isLoading,
    error,
  } = useQuery({
    queryKey: [...salesKeys.invoices(), invoiceId],
    queryFn: () => invoiceService.getInvoiceById(invoiceId),
    select: (res) => res.data,
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-4">
            <div className="h-16 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-[400px] animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
          </div>
          <div className="space-y-4">
            <div className="h-40 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-60 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !invoice) {
    return (
      <div className="flex min-h-[300px] flex-col items-center justify-center gap-3">
        <p className="text-lg font-medium">Invoice not found</p>
        <Link href="/invoices">
          <Button variant="outline">Back to Invoices</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <InvoiceHeaderSection invoice={invoice} />

      {/* Two-column layout */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left Column — PDF + Items */}
        <div className="space-y-6 lg:col-span-2">
          <InvoicePDFPreview invoiceId={invoiceId} />

          {/* Action buttons */}
          <div className="flex items-center gap-2">
            <DownloadPDFButton invoiceId={invoiceId} invoiceNumber={invoice.invoiceNumber} />
            <PrintInvoiceButton />
          </div>

          {/* Line Items */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Line Items</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Product</TableHead>
                    <TableHead>SKU</TableHead>
                    <TableHead className="text-right">Qty</TableHead>
                    <TableHead className="text-right">Unit Price</TableHead>
                    <TableHead className="text-right">Tax</TableHead>
                    <TableHead className="text-right">Total</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {invoice.items.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium">{item.productName}</TableCell>
                      <TableCell className="text-gray-500 font-mono text-xs">{item.sku}</TableCell>
                      <TableCell className="text-right">{item.quantity}</TableCell>
                      <TableCell className="text-right">{formatCurrency(item.unitPrice)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(item.taxAmount)}</TableCell>
                      <TableCell className="text-right font-medium">
                        {formatCurrency(item.lineTotal)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Summary */}
          <Card>
            <CardContent className="space-y-2 pt-6 text-sm">
              <div className="flex justify-between">
                <span>Subtotal</span>
                <span>{formatCurrency(invoice.subtotal)}</span>
              </div>
              {invoice.discountTotal > 0 && (
                <div className="flex justify-between text-red-600">
                  <span>Discount</span>
                  <span>-{formatCurrency(invoice.discountTotal)}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span>Tax</span>
                <span>{formatCurrency(invoice.taxTotal)}</span>
              </div>
              <div className="flex justify-between border-t pt-2 text-base font-bold">
                <span>Total</span>
                <span>{formatCurrency(invoice.total)}</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column — Actions + Payment */}
        <div className="space-y-6 lg:sticky lg:top-20 lg:self-start">
          {/* Quick Actions */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-2">
              <Button variant="outline" size="sm" onClick={() => setSendModalOpen(true)}>
                <Send className="mr-2 h-4 w-4" />
                Send
              </Button>
              <DownloadPDFButton invoiceId={invoiceId} invoiceNumber={invoice.invoiceNumber} />
              <PrintInvoiceButton />
              <Button variant="outline" size="sm">
                <CreditCard className="mr-2 h-4 w-4" />
                Payment
              </Button>
            </CardContent>
          </Card>

          {/* Invoice Summary */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Invoice Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1.5 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Total</span>
                <span className="font-medium">{formatCurrency(invoice.total)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Paid</span>
                <span className="font-medium text-green-600">
                  {formatCurrency(invoice.amountPaid)}
                </span>
              </div>
              <div className="flex justify-between border-t pt-1.5">
                <span className="font-medium">Balance</span>
                <span
                  className={`font-bold ${
                    invoice.balanceDue > 0 ? 'text-red-600' : 'text-green-600'
                  }`}
                >
                  {formatCurrency(invoice.balanceDue)}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Payment History */}
          <PaymentHistory
            payments={[]}
            totalAmount={invoice.total}
            amountPaid={invoice.amountPaid}
            balanceDue={invoice.balanceDue}
          />
        </div>
      </div>

      {/* Notes */}
      {invoice.notes && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Notes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 dark:text-gray-400">{invoice.notes}</p>
          </CardContent>
        </Card>
      )}

      {/* Send Modal */}
      <SendInvoiceModal
        isOpen={sendModalOpen}
        onClose={() => setSendModalOpen(false)}
        invoice={invoice}
        onSend={async (data) => {
          await invoiceService.sendInvoice(invoiceId, data.to);
          setSendModalOpen(false);
        }}
      />
    </div>
  );
}
