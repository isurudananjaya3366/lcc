'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface OrderTotalsProps {
  subtotal: number;
  discount?: number;
  tax: number;
  shipping?: number;
  total: number;
  paymentStatus?: 'paid' | 'partial' | 'unpaid';
  paidAmount?: number;
}

function formatCurrency(amount: number): string {
  return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

export function OrderTotals({
  subtotal,
  discount = 0,
  tax,
  shipping = 0,
  total,
  paymentStatus,
  paidAmount = 0,
}: OrderTotalsProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="ml-auto max-w-sm space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">Subtotal</span>
            <span>{formatCurrency(subtotal)}</span>
          </div>

          {discount > 0 && (
            <div className="flex justify-between text-red-600">
              <span>Discount</span>
              <span>- {formatCurrency(discount)}</span>
            </div>
          )}

          <div className="flex justify-between">
            <span className="text-gray-500">Tax</span>
            <span>{formatCurrency(tax)}</span>
          </div>

          {shipping > 0 && (
            <div className="flex justify-between">
              <span className="text-gray-500">Shipping</span>
              <span>{formatCurrency(shipping)}</span>
            </div>
          )}

          <div className="flex justify-between border-t pt-2 text-base font-bold">
            <span>Grand Total</span>
            <span>{formatCurrency(total)}</span>
          </div>

          {paymentStatus && (
            <div className="flex items-center justify-between border-t pt-2">
              <span className="text-gray-500">Payment</span>
              <div className="flex items-center gap-2">
                {paymentStatus === 'paid' && (
                  <Badge className="bg-green-100 text-green-800" variant="secondary">
                    Paid
                  </Badge>
                )}
                {paymentStatus === 'partial' && (
                  <>
                    <Badge className="bg-yellow-100 text-yellow-800" variant="secondary">
                      Partially Paid
                    </Badge>
                    <span className="text-xs text-gray-500">
                      {formatCurrency(paidAmount)} of {formatCurrency(total)}
                    </span>
                  </>
                )}
                {paymentStatus === 'unpaid' && (
                  <Badge className="bg-red-100 text-red-800" variant="secondary">
                    Unpaid
                  </Badge>
                )}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
