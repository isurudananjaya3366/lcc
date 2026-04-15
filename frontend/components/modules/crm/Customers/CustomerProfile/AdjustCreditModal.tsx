'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { AlertTriangle, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { customerKeys } from '@/lib/queryKeys';
import customerService from '@/services/api/customerService';
import type { Customer } from '@/types/customer';

interface AdjustCreditModalProps {
  customer: Customer;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

function formatLKR(amount: number): string {
  return `₨${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

const reasons = [
  { value: 'business_growth', label: 'Business Growth' },
  { value: 'good_payment_history', label: 'Good Payment History' },
  { value: 'large_order_request', label: 'Large Order Request' },
  { value: 'risk_reduction', label: 'Risk Reduction' },
  { value: 'credit_review', label: 'Credit Review' },
  { value: 'other', label: 'Other' },
];

export function AdjustCreditModal({
  customer,
  isOpen,
  onClose,
  onSuccess,
}: AdjustCreditModalProps) {
  const queryClient = useQueryClient();
  const currentLimit = customer.creditLimit?.creditLimit ?? 0;

  const [newLimit, setNewLimit] = useState(currentLimit.toString());
  const [reason, setReason] = useState('');
  const [notes, setNotes] = useState('');

  const newLimitNum = parseFloat(newLimit) || 0;
  const change = newLimitNum - currentLimit;
  const changePercent = currentLimit > 0 ? (change / currentLimit) * 100 : 0;
  const isIncrease = change > 0;

  function getApprovalLevel() {
    if (!isIncrease) return null;
    if (changePercent > 100) return { level: 'Director', variant: 'destructive' as const };
    if (changePercent >= 50) return { level: 'Manager', variant: 'default' as const };
    return null;
  }

  const approvalLevel = getApprovalLevel();

  const mutation = useMutation({
    mutationFn: () =>
      customerService.updateCustomerCredit(customer.id, {
        creditLimit: newLimitNum,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: customerKeys.detail(customer.id) });
      onSuccess?.();
      onClose();
    },
  });

  const isValid = newLimitNum >= 0 && (isIncrease ? reason.length > 0 : true);

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Adjust Credit Limit</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="rounded-lg bg-muted p-4 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Current Limit</span>
              <span className="font-medium">{formatLKR(currentLimit)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Used</span>
              <span>{formatLKR(customer.creditLimit?.currentBalance ?? 0)}</span>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="new-limit">New Credit Limit (₨) *</Label>
            <Input
              id="new-limit"
              type="number"
              min="0"
              step="1000"
              value={newLimit}
              onChange={(e) => setNewLimit(e.target.value)}
            />
            {change !== 0 && (
              <p className={`text-sm ${isIncrease ? 'text-green-600' : 'text-red-500'}`}>
                {isIncrease ? '+' : ''}
                {formatLKR(change)} ({isIncrease ? '+' : ''}
                {changePercent.toFixed(0)}%)
              </p>
            )}
          </div>

          {approvalLevel && (
            <Alert variant={approvalLevel.variant}>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                This increase requires <strong>{approvalLevel.level} approval</strong>.
              </AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="credit-reason">Reason {isIncrease ? '*' : ''}</Label>
            <Select value={reason} onValueChange={setReason}>
              <SelectTrigger id="credit-reason">
                <SelectValue placeholder="Select reason" />
              </SelectTrigger>
              <SelectContent>
                {reasons.map((r) => (
                  <SelectItem key={r.value} value={r.value}>
                    {r.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="credit-notes">Additional Notes</Label>
            <Textarea
              id="credit-notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              maxLength={500}
              rows={3}
              placeholder="Optional notes..."
            />
            <p className="text-xs text-muted-foreground">{notes.length}/500</p>
          </div>

          {!isIncrease && change < 0 && (
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                Reducing the credit limit may affect the customer&apos;s ability to place new
                orders.
              </AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={() => mutation.mutate()} disabled={!isValid || mutation.isPending}>
            {mutation.isPending ? 'Adjusting...' : 'Adjust Credit'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
