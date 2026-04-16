'use client';

import React, { useState, type FC } from 'react';
import { cn } from '@/lib/utils';
import FooterLink from './FooterLink';

interface LinkItem {
  label: string;
  href: string;
}

interface FooterLinkColumnProps {
  title: string;
  links: LinkItem[];
  collapsible?: boolean;
  className?: string;
}

const FooterLinkColumn: FC<FooterLinkColumnProps> = ({
  title,
  links,
  collapsible = true,
  className,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className={cn('', className)}>
      {/* Title - clickable on mobile when collapsible */}
      <button
        type="button"
        onClick={() => collapsible && setIsOpen(!isOpen)}
        className={cn(
          'flex items-center justify-between w-full text-sm font-semibold text-white uppercase tracking-wider',
          collapsible ? 'md:cursor-default' : 'cursor-default'
        )}
        aria-expanded={collapsible ? isOpen : undefined}
      >
        {title}
        {collapsible && (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className={cn(
              'h-4 w-4 md:hidden transition-transform duration-200',
              isOpen && 'rotate-180'
            )}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        )}
      </button>

      {/* Links - always visible on desktop, collapsible on mobile */}
      <ul className={cn('mt-4 space-y-3', collapsible && !isOpen && 'hidden md:block')}>
        {links.map((link) => (
          <li key={link.href}>
            <FooterLink href={link.href}>{link.label}</FooterLink>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FooterLinkColumn;
