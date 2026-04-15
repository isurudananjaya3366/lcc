interface ChangeCalculatorProps {
  tendered: number;
  due: number;
}

export function ChangeCalculator({ tendered, due }: ChangeCalculatorProps) {
  const change = Math.max(0, tendered - due);

  if (tendered < due) {
    const shortfall = due - tendered;
    return (
      <div className="rounded-md bg-amber-50 px-3 py-2 text-center dark:bg-amber-950">
        <p className="text-xs text-amber-600 dark:text-amber-400">Short by</p>
        <p className="text-lg font-bold text-amber-700 dark:text-amber-300">
          ₨ {shortfall.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-md bg-green-50 px-3 py-2 text-center dark:bg-green-950">
      <p className="text-xs text-green-600 dark:text-green-400">Change Due</p>
      <p className="text-lg font-bold text-green-700 dark:text-green-300">
        ₨ {change.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
      </p>
    </div>
  );
}
