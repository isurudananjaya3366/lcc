'use client';

import { CreditCard, Banknote, Building2, FileText, Copy } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface Payment {
  id: string;
  date: string;
  method: string;
  amount: number;
  reference?: string;
  balance: number;
}

interface PaymentHistoryProps {
  payments: Payment[];
  totalAmount: number;
  amountPaid: number;
  balanceDue: number;
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

const methodIcons: Record<string, React.ElementType> = {
  cash: Banknote,
  card: CreditCard,
  bank_transfer: Building2,
  cheque: FileText,
};

function getMethodIcon(method: string): React.ElementType {
  return methodIcons[method.toLowerCase()] || CreditCard;
}

function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text);
}

export function PaymentHistory({
  payments,
  totalAmount,
  amountPaid,
  balanceDue,
}: PaymentHistoryProps) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Payment History</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Summary */}
        <div className="space-y-1.5 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">Total</span>
            <span className="font-medium">{formatCurrency(totalAmount)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Paid</span>
            <span className="font-medium text-green-600">{formatCurrency(amountPaid)}</span>
          </div>
          <div className="flex justify-between border-t pt-1.5">
            <span className="font-medium">Balance Due</span>
            <span className={`font-bold ${balanceDue > 0 ? 'text-red-600' : 'text-green-600'}`}>
              {formatCurrency(balanceDue)}
            </span>
          </div>
        </div>

        {/* Payment List */}
        {payments.length === 0 ? (
          <p className="text-center text-sm text-gray-500 py-4">No payments recorded</p>
        ) : (
          <div className="space-y-3">
            {payments.map((payment) => {
              const Icon = getMethodIcon(payment.method);
              return (
                <div key={payment.id} className="flex items-start gap-3 rounded-md border p-3">
                  <div className="mt-0.5 flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
                    <Icon className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{formatCurrency(payment.amount)}</span>
                      <Badge variant="secondary" className="text-xs capitalize">
                        {payment.method.replace(/_/g, ' ')}
                      </Badge>
                    </div>
                    <p className="text-xs text-gray-500">{formatDate(payment.date)}</p>
                    {payment.reference && (
                      <button
                        onClick={() => copyToClipboard(payment.reference!)}
                        className="mt-1 flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600"
                      >
                        <span className="truncate max-w-[120px]">Ref: {payment.reference}</span>
                        <Copy className="h-3 w-3 flex-shrink-0" />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
