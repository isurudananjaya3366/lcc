import React, { type FC } from 'react';
import { cn } from '@/lib/utils';

const paymentMethods = [
  { name: 'Visa', alt: 'Visa', type: 'text' as const },
  { name: 'Mastercard', alt: 'Mastercard', type: 'text' as const },
  { name: 'PayHere', alt: 'PayHere', type: 'text' as const, highlight: true },
  { name: 'COD', alt: 'Cash on Delivery', type: 'icon' as const },
  { name: 'Bank', alt: 'Bank Transfer', type: 'icon' as const },
];

interface PaymentIconsProps {
  className?: string;
}

const PaymentIcons: FC<PaymentIconsProps> = ({ className }) => {
  return (
    <div className={cn('', className)} aria-label="Accepted payment methods">
      <div className="flex items-center gap-3 flex-wrap justify-center md:justify-end">
        {paymentMethods.map((method) => (
          <span
            key={method.name}
            className={cn(
              'inline-flex items-center px-2.5 py-1.5 rounded text-xs font-medium transition-all duration-200',
              method.highlight
                ? 'bg-white/20 text-white'
                : 'bg-white/10 text-gray-400 hover:bg-white/20 hover:text-white'
            )}
            aria-label={method.alt}
          >
            {method.type === 'icon' ? (
              <span className="flex items-center gap-1">
                {method.name === 'COD' && (
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                )}
                {method.name === 'Bank' && (
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                )}
                {method.alt}
              </span>
            ) : (
              method.name
            )}
          </span>
        ))}
      </div>
    </div>
  );
};

export default PaymentIcons;
