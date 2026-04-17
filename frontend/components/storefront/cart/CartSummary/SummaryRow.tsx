import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import { formatCurrency } from '@/lib/store/config';

interface SummaryRowProps {
  label: string;
  value: number;
  isDiscount?: boolean;
  isTotal?: boolean;
  isEstimate?: boolean;
  className?: string;
}

const SummaryRow: FC<SummaryRowProps> = ({
  label,
  value,
  isDiscount = false,
  isTotal = false,
  isEstimate = false,
  className,
}) => {
  return (
    <div
      className={cn(
        'flex items-center justify-between',
        isTotal && 'border-t border-gray-200 pt-3 dark:border-gray-700',
        className
      )}
    >
      <span
        className={cn(
          'text-sm text-gray-600 dark:text-gray-400',
          isTotal && 'text-base font-semibold text-gray-900 dark:text-gray-100'
        )}
      >
        {label}
      </span>

      {isEstimate ? (
        <span className="text-sm italic text-gray-400 dark:text-gray-500">
          Calculated at checkout
        </span>
      ) : (
        <span
          className={cn(
            'text-sm text-gray-900 dark:text-gray-100',
            isDiscount && 'text-green-600 dark:text-green-400',
            isTotal && 'text-base font-semibold'
          )}
        >
          {isDiscount && value > 0 ? `−${formatCurrency(value)}` : formatCurrency(value)}
        </span>
      )}
    </div>
  );
};

export default SummaryRow;
