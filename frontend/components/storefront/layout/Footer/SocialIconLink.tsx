import React, { type FC } from 'react';
import { cn } from '@/lib/utils';

interface SocialIconLinkProps {
  href: string;
  icon: React.ReactNode;
  label: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeClasses = {
  sm: 'p-2',
  md: 'p-2.5',
  lg: 'p-3',
};

const SocialIconLink: FC<SocialIconLinkProps> = ({ href, icon, label, size = 'md', className }) => {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className={cn(
        'inline-flex items-center justify-center rounded-lg text-gray-400 bg-white/10',
        'hover:bg-white/20 hover:text-white hover:scale-110',
        'focus:outline-none focus:ring-2 focus:ring-white',
        'active:bg-white/30 active:scale-95',
        'transition-all duration-200 ease-in-out',
        sizeClasses[size],
        className
      )}
      aria-label={label}
    >
      {icon}
    </a>
  );
};

export default SocialIconLink;
