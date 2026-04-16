import React, { type FC } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';

interface CopyrightProps {
  companyName?: string;
  showLinks?: boolean;
  className?: string;
}

const Copyright: FC<CopyrightProps> = ({
  companyName = 'LankaCommerce',
  showLinks = false,
  className,
}) => {
  const currentYear = new Date().getFullYear();

  return (
    <p className={cn('text-sm text-gray-400 text-center md:text-left', className)}>
      © {currentYear} {companyName}. All rights reserved.
      {showLinks && (
        <span className="block md:inline md:ml-2 mt-1 md:mt-0">
          <Link href="/privacy" className="hover:text-gray-300 transition-colors">
            Privacy Policy
          </Link>
          <span className="mx-2">•</span>
          <Link href="/terms" className="hover:text-gray-300 transition-colors">
            Terms of Service
          </Link>
        </span>
      )}
    </p>
  );
};

export default Copyright;
