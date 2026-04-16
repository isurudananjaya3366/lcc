import React, { type FC } from 'react';
import Link from 'next/link';

const FooterLogo: FC = () => {
  return (
    <div className="space-y-4">
      {/* Logo / Brand Name */}
      <Link href="/" className="inline-block">
        <span className="text-xl font-bold text-white">
          Lanka<span className="text-green-400">Commerce</span>
        </span>
      </Link>

      {/* Store description */}
      <p className="text-sm text-gray-400 leading-relaxed max-w-xs">
        Your trusted online marketplace in Sri Lanka. Quality products, fast delivery, and secure
        payments.
      </p>

      {/* Address */}
      <div className="flex items-start gap-2 text-sm text-gray-500">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-4 w-4 mt-0.5 flex-shrink-0"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
        <span>Colombo, Sri Lanka</span>
      </div>
    </div>
  );
};

export default FooterLogo;
