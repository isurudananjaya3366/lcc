import { CheckCircle } from 'lucide-react';

interface PendingAmountDisplayProps {
  grandTotal: number;
  paidAmount: number;
}

export function PendingAmountDisplay({ grandTotal, paidAmount }: PendingAmountDisplayProps) {
  const pending = grandTotal - paidAmount;

  // Paid in Full
  if (pending === 0 && paidAmount > 0) {
    return (
      <div className="flex items-center justify-between text-sm font-medium text-green-600 dark:text-green-400">
        <span className="flex items-center gap-1">
          <CheckCircle className="h-3.5 w-3.5" />
          Paid in Full
        </span>
        <span>✓</span>
      </div>
    );
  }

  // Change Due (overpaid)
  if (pending < 0) {
    return (
      <div className="flex justify-between text-sm font-medium text-blue-600 dark:text-blue-400">
        <span>Change Due</span>
        <span>₨ {Math.abs(pending).toLocaleString('en-LK', { minimumFractionDigits: 2 })}</span>
      </div>
    );
  }

  // No payment yet
  if (paidAmount === 0) return null;

  // Balance due (underpaid)
  return (
    <div className="flex justify-between text-sm font-medium text-red-600 dark:text-red-400">
      <span>Balance Due</span>
      <span>₨ {pending.toLocaleString('en-LK', { minimumFractionDigits: 2 })}</span>
    </div>
  );
}
