import React, { type FC } from 'react';
import { cn } from '@/lib/utils';

interface SecureCheckoutNoteProps {
  className?: string;
}

const SecureCheckoutNote: FC<SecureCheckoutNoteProps> = ({ className }) => {
  return (
    <div className={cn('flex items-center justify-center gap-1.5 text-xs text-gray-400 dark:text-gray-500', className)}>
      {/* Lock icon */}
      <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
        />
      </svg>
      <span>Secure checkout with 256-bit SSL encryption</span>
    </div>
  );
};

export default SecureCheckoutNote;
