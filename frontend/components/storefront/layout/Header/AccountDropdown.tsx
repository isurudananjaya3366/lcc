'use client';

import React, { useRef, useEffect, type FC } from 'react';
import { cn } from '@/lib/utils';
import type { AccountDropdownProps } from '@/types/store/header';
import LoginRegisterLinks from './LoginRegisterLinks';
import LoggedInMenu from './LoggedInMenu';

const AccountDropdown: FC<AccountDropdownProps> = ({
  isOpen,
  isLoggedIn,
  onClose,
  userName,
  userEmail,
  className,
}) => {
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      ref={dropdownRef}
      className={cn(
        'absolute right-0 top-full mt-2 w-64 bg-white dark:bg-gray-900 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50',
        'animate-in zoom-in-95 fade-in duration-150',
        className
      )}
      role="menu"
      aria-label="Account menu"
    >
      {isLoggedIn ? (
        <>
          {(userName || userEmail) && (
            <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-800">
              {userName && (
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                  {userName}
                </p>
              )}
              {userEmail && (
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{userEmail}</p>
              )}
            </div>
          )}
          <LoggedInMenu onClose={onClose} />
        </>
      ) : (
        <LoginRegisterLinks onClose={onClose} />
      )}
    </div>
  );
};

export default AccountDropdown;
