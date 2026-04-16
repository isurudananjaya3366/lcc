import React, { type FC } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';

interface FooterLinkProps {
  href: string;
  children: React.ReactNode;
  className?: string;
}

const FooterLink: FC<FooterLinkProps> = ({ href, children, className }) => {
  const isExternal = href.startsWith('http');

  if (isExternal) {
    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className={cn(
          'block text-sm text-gray-400 hover:text-white transition-colors duration-200',
          'focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-900 rounded',
          className
        )}
      >
        {children}
      </a>
    );
  }

  return (
    <Link
      href={href}
      className={cn(
        'block text-sm text-gray-400 hover:text-white transition-colors duration-200',
        'focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-900 rounded',
        className
      )}
    >
      {children}
    </Link>
  );
};

export default FooterLink;
