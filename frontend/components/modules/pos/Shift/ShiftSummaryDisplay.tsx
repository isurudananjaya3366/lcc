'use client';

interface ShiftSummaryDisplayProps {
  sessionNumber: string;
  transactionCount: number;
  totalSales: number;
  expectedCash: number;
  openingCash?: number;
  startTime?: string;
}

export function ShiftSummaryDisplay({
  sessionNumber,
  transactionCount,
  totalSales,
  expectedCash,
  openingCash,
  startTime,
}: ShiftSummaryDisplayProps) {
  const fmt = (n: number) => `₨ ${n.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;

  const duration = startTime
    ? (() => {
        const diff = Date.now() - new Date(startTime).getTime();
        const hrs = Math.floor(diff / 3600000);
        const mins = Math.floor((diff % 3600000) / 60000);
        return `${hrs}h ${mins}m`;
      })()
    : null;

  return (
    <div className="rounded-md bg-gray-50 p-3 text-sm dark:bg-gray-800">
      <div className="grid grid-cols-2 gap-2">
        <div>
          <p className="text-[10px] font-medium uppercase text-gray-500">Shift</p>
          <p className="font-medium">{sessionNumber}</p>
        </div>
        <div>
          <p className="text-[10px] font-medium uppercase text-gray-500">Transactions</p>
          <p className="font-medium">{transactionCount}</p>
        </div>
        {duration && (
          <div>
            <p className="text-[10px] font-medium uppercase text-gray-500">Duration</p>
            <p className="font-medium">{duration}</p>
          </div>
        )}
        {openingCash != null && (
          <div>
            <p className="text-[10px] font-medium uppercase text-gray-500">Opening Cash</p>
            <p className="font-medium">{fmt(openingCash)}</p>
          </div>
        )}
        <div>
          <p className="text-[10px] font-medium uppercase text-gray-500">Sales</p>
          <p className="font-medium">{fmt(totalSales)}</p>
        </div>
        <div>
          <p className="text-[10px] font-medium uppercase text-gray-500">Expected Cash</p>
          <p className="font-medium">{fmt(expectedCash)}</p>
        </div>
      </div>
    </div>
  );
}
