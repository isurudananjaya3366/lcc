import React, { type FC } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { cn } from '@/lib/utils';
import type { LogoProps } from '@/types/store/header';
import { handleLogoError } from './logoUtils';

const Logo: FC<LogoProps> = ({ src, alt = 'LankaCommerce Store', href = '/', className }) => {
  return (
    <Link
      href={href}
      className={cn(
        'flex items-center gap-2 shrink-0 hover:opacity-80 transition-opacity focus:outline-none focus:ring-2 focus:ring-green-500 rounded',
        className
      )}
      aria-label="Go to homepage"
      prefetch={true}
    >
      {src ? (
        <Image
          src={src}
          alt={alt}
          width={120}
          height={40}
          className="h-8 md:h-9 lg:h-10 w-auto"
          onError={handleLogoError}
          priority
        />
      ) : (
        <span className="text-xl md:text-2xl font-bold text-green-700 dark:text-green-400">
          Lanka<span className="text-gray-900 dark:text-white">Commerce</span>
        </span>
      )}
    </Link>
  );
};

export default Logo;
