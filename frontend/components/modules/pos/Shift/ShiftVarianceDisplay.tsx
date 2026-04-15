interface ShiftVarianceDisplayProps {
  expected: number;
  actual: number;
  variance: number;
  openingCash?: number;
  cashSales?: number;
  cashRefunds?: number;
}

export function ShiftVarianceDisplay({
  expected,
  actual,
  variance,
  openingCash,
  cashSales,
  cashRefunds,
}: ShiftVarianceDisplayProps) {
  const abs = Math.abs(variance);
  const pct = expected > 0 ? (abs / expected) * 100 : 0;

  let color: string;
  let status: string;
  let icon: string;
  let recommendation: string;

  if (abs === 0) {
    color = 'text-green-600 bg-green-50 dark:bg-green-950 dark:text-green-400';
    status = 'Perfect Match';
    icon = '✓';
    recommendation = 'No action needed.';
  } else if (abs < 10) {
    color = 'text-green-600 bg-green-50 dark:bg-green-950 dark:text-green-400';
    status = 'Acceptable';
    icon = '✓';
    recommendation = 'No action needed.';
  } else if (abs < 100) {
    color = 'text-yellow-600 bg-yellow-50 dark:bg-yellow-950 dark:text-yellow-400';
    status = 'Minor Discrepancy';
    icon = '⚠️';
    recommendation = 'Document in closing notes.';
  } else if (abs < 500) {
    color = 'text-orange-600 bg-orange-50 dark:bg-orange-950 dark:text-orange-400';
    status = 'Investigate';
    icon = '⚠️';
    recommendation = 'Review transactions and document reason.';
  } else {
    color = 'text-red-600 bg-red-50 dark:bg-red-950 dark:text-red-400';
    status = 'Major Discrepancy';
    icon = '🚨';
    recommendation = 'Manager review required.';
  }

  const fmt = (n: number) => n.toLocaleString('en-LK', { minimumFractionDigits: 2 });

  return (
    <div className={`rounded-md p-3 ${color}`}>
      <div className="flex items-center justify-between text-sm font-medium">
        <span>
          {icon} {status}
        </span>
        <span>
          {variance >= 0 ? '+' : '-'}₨ {fmt(abs)} ({pct.toFixed(2)}%)
        </span>
      </div>

      {/* Breakdown */}
      <div className="mt-2 space-y-0.5 text-xs opacity-80">
        {openingCash != null && (
          <div className="flex justify-between">
            <span>Opening Cash</span>
            <span>₨ {fmt(openingCash)}</span>
          </div>
        )}
        {cashSales != null && (
          <div className="flex justify-between">
            <span>+ Cash Sales</span>
            <span>₨ {fmt(cashSales)}</span>
          </div>
        )}
        {cashRefunds != null && cashRefunds > 0 && (
          <div className="flex justify-between">
            <span>- Cash Refunds</span>
            <span>₨ {fmt(cashRefunds)}</span>
          </div>
        )}
        <div className="flex justify-between border-t border-current/20 pt-0.5 font-medium">
          <span>Expected Cash</span>
          <span>₨ {fmt(expected)}</span>
        </div>
        <div className="flex justify-between font-medium">
          <span>Actual Cash</span>
          <span>₨ {fmt(actual)}</span>
        </div>
      </div>

      {/* Recommendation */}
      <p className="mt-2 text-xs italic opacity-70">{recommendation}</p>
    </div>
  );
}
