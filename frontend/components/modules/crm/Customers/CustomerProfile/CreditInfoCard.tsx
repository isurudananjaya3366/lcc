'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';

interface CreditInfoCardProps {
  customer: {
    creditLimit: number;
    creditUsed: number;
    paymentTerms?: string;
  };
  onAdjustCredit?: () => void;
  editable?: boolean;
}

function formatLKR(amount: number): string {
  return `₨${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

function getCreditStatus(usedPercent: number, limit: number) {
  if (limit === 0) return { label: 'No Credit', color: 'secondary' as const };
  if (usedPercent > 100) return { label: 'Over Limit', color: 'destructive' as const };
  if (usedPercent >= 70) return { label: 'Near Limit', color: 'pending' as const };
  return { label: 'Good Standing', color: 'default' as const };
}

function getProgressColor(usedPercent: number): string {
  if (usedPercent > 100) return '[&>div]:bg-red-500';
  if (usedPercent >= 70) return '[&>div]:bg-yellow-500';
  return '[&>div]:bg-green-500';
}

export function CreditInfoCard({ customer, onAdjustCredit, editable }: CreditInfoCardProps) {
  const usedPercent =
    customer.creditLimit > 0 ? (customer.creditUsed / customer.creditLimit) * 100 : 0;
  const available = customer.creditLimit - customer.creditUsed;
  const status = getCreditStatus(usedPercent, customer.creditLimit);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-base font-medium">Credit Information</CardTitle>
        {editable && (
          <Button variant="ghost" size="sm" onClick={onAdjustCredit}>
            Adjust
          </Button>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Credit Limit</span>
          <span className="text-sm font-medium">{formatLKR(customer.creditLimit)}</span>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Used</span>
            <span>
              {formatLKR(customer.creditUsed)} ({Math.round(usedPercent)}%)
            </span>
          </div>
          <Progress
            value={Math.min(usedPercent, 100)}
            className={`h-2 ${getProgressColor(usedPercent)}`}
          />
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Available</span>
          <span
            className={`text-sm font-medium ${available < 0 ? 'text-red-500' : 'text-green-600'}`}
          >
            {formatLKR(available)}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Status</span>
          <Badge variant={status.color}>{status.label}</Badge>
        </div>

        {customer.paymentTerms && (
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Payment Terms</span>
            <span className="text-sm">{customer.paymentTerms.replace(/_/g, ' ')}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
