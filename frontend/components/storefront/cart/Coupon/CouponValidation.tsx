import React, { type FC } from 'react';
import { cn } from '@/lib/utils';

interface CouponValidationProps {
  error: string | null;
  success: string | null;
  className?: string;
}

const CouponValidation: FC<CouponValidationProps> = ({ error, success, className }) => {
  if (!error && !success) return null;

  return (
    <div className={cn('mt-1.5 text-sm', className)}>
      {error && <p className="text-red-600 dark:text-red-400">{error}</p>}
      {success && <p className="text-green-600 dark:text-green-400">{success}</p>}
    </div>
  );
};

export default CouponValidation;
