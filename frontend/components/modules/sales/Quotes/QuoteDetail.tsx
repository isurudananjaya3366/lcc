'use client';

import { useState } from 'react';
import { useQuoteDetails } from '@/hooks/queries/useQuotes';
import { useQuoteConversion } from '@/hooks/sales/useQuoteConversion';
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
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { QuoteDetailsHeader } from './QuoteDetailsHeader';
import { ConversionModal } from './ConversionModal';

interface QuoteDetailProps {
  quoteId: string;
}

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

export function QuoteDetail({ quoteId }: QuoteDetailProps) {
  const { data: quote, isLoading, error } = useQuoteDetails(quoteId);
  const conversion = useQuoteConversion();
  const [conversionModalOpen, setConversionModalOpen] = useState(false);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-64 w-full animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
      </div>
    );
  }

  if (error || !quote) {
    return (
      <div className="flex min-h-[300px] flex-col items-center justify-center gap-3">
        <p className="text-lg font-medium">Quote not found</p>
        <Link href="/quotes">
          <Button variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Quotes
          </Button>
        </Link>
      </div>
    );
  }

  const isExpired = new Date(quote.expiryDate) < new Date();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/quotes">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
      </div>

      <QuoteDetailsHeader quote={quote} onConvert={() => setConversionModalOpen(true)} />

      {/* Validity Info */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          {/* Customer */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Customer</CardTitle>
            </CardHeader>
            <CardContent className="text-sm">
              <p className="font-medium">{quote.customerName}</p>
              {quote.customerEmail && <p className="text-gray-500">{quote.customerEmail}</p>}
            </CardContent>
          </Card>

          {/* Items */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Quote Items</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Product</TableHead>
                    <TableHead>SKU</TableHead>
                    <TableHead className="text-right">Qty</TableHead>
                    <TableHead className="text-right">Unit Price</TableHead>
                    <TableHead className="text-right">Discount</TableHead>
                    <TableHead className="text-right">Total</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {quote.items.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium">{item.productName}</TableCell>
                      <TableCell className="font-mono text-xs text-gray-500">{item.sku}</TableCell>
                      <TableCell className="text-right">{item.quantity}</TableCell>
                      <TableCell className="text-right">{formatCurrency(item.unitPrice)}</TableCell>
                      <TableCell className="text-right">
                        {item.discountPercent > 0 ? `${item.discountPercent}%` : '—'}
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        {formatCurrency(item.total)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Pricing Summary */}
          <Card>
            <CardContent className="space-y-2 pt-6 text-sm">
              <div className="flex justify-between">
                <span>Subtotal</span>
                <span>{formatCurrency(quote.subtotal)}</span>
              </div>
              {quote.discountTotal > 0 && (
                <div className="flex justify-between text-red-600">
                  <span>Discount</span>
                  <span>-{formatCurrency(quote.discountTotal)}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span>Tax</span>
                <span>{formatCurrency(quote.taxTotal)}</span>
              </div>
              <div className="flex justify-between border-t pt-2 text-base font-bold">
                <span>Total</span>
                <span>{formatCurrency(quote.total)}</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right sidebar */}
        <div className="space-y-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Quote Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Created</span>
                <span>{formatDate(quote.createdAt)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Quote Date</span>
                <span>{formatDate(quote.quoteDate)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Expiry</span>
                <span className={isExpired ? 'text-red-600 font-medium' : ''}>
                  {formatDate(quote.expiryDate)}
                  {isExpired && ' (Expired)'}
                </span>
              </div>
              {quote.orderId && (
                <div className="flex justify-between border-t pt-2">
                  <span className="text-gray-500">Order</span>
                  <Link href={`/orders/${quote.orderId}`} className="text-blue-600 hover:underline">
                    View Order
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>

          {quote.terms && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Terms & Conditions</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
                  {quote.terms}
                </p>
              </CardContent>
            </Card>
          )}

          {quote.notes && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Notes</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
                  {quote.notes}
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Conversion Modal */}
      <ConversionModal
        isOpen={conversionModalOpen}
        onClose={() => setConversionModalOpen(false)}
        quote={quote}
        isConverting={conversion.isPending}
        onConvert={async (options) => {
          await conversion.mutateAsync({
            quoteId: quote.id,
            ...options,
          });
          setConversionModalOpen(false);
        }}
      />
    </div>
  );
}
