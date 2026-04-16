'use client';

import React, { type FC } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';

interface AccountLinkProps {
  isLoggedIn: boolean;
  userName?: string;
  onClick: () => void;
  className?: string;
}

const AccountLink: FC<AccountLinkProps> = ({ isLoggedIn, userName, onClick, className }) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'flex items-center gap-1.5 p-2 text-gray-700 dark:text-gray-300 hover:text-green-700 dark:hover:text-green-400 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800',
        className
      )}
      aria-label={isLoggedIn ? `Account menu for ${userName}` : 'Login or register'}
      aria-haspopup="true"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-5 w-5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
        />
      </svg>
      <span className="hidden md:inline text-sm font-medium truncate max-w-[100px]">
        {isLoggedIn ? userName : 'Login'}
      </span>
    </button>
  );
};

export default AccountLink;
