interface PaymentAmountProps {
  total: number;
  paid: number;
  remaining: number;
}

export function PaymentAmount({ total, paid, remaining }: PaymentAmountProps) {
  return (
    <div className="rounded-lg bg-gray-50 p-4 text-center dark:bg-gray-800">
      <p className="text-xs font-medium uppercase text-gray-500 dark:text-gray-400">Amount Due</p>
      <p className="mt-1 text-3xl font-bold text-gray-900 dark:text-gray-100">
        ₨ {remaining.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
      </p>
      {paid > 0 && (
        <p className="mt-1 text-xs text-green-600">
          ₨ {paid.toLocaleString('en-LK', { minimumFractionDigits: 2 })} paid of ₨{' '}
          {total.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
        </p>
      )}
    </div>
  );
}
