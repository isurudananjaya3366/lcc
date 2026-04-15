'use client';

import { useState, useEffect } from 'react';
import { Clock, Store } from 'lucide-react';
import { ExitPOSButton } from './ExitPOSButton';
import { ShiftStatus } from './ShiftStatus';

export function POSHeader() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60_000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-gray-200 bg-white px-4 dark:border-gray-800 dark:bg-gray-900">
      {/* Left Section */}
      <div className="flex items-center gap-3">
        <Store className="h-6 w-6 text-primary" />
        <div>
          <h1 className="text-base font-semibold text-gray-900 dark:text-gray-100">POS Terminal</h1>
          <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
            <Clock className="h-3 w-3" />
            <time dateTime={currentTime.toISOString()}>
              {currentTime.toLocaleDateString('en-LK', {
                weekday: 'short',
                day: 'numeric',
                month: 'short',
              })}{' '}
              {currentTime.toLocaleTimeString('en-LK', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </time>
          </div>
        </div>
      </div>

      {/* Center Section */}
      <div className="hidden md:block">
        <ShiftStatus />
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-3">
        <div className="block md:hidden">
          <ShiftStatus compact />
        </div>
        <ExitPOSButton />
      </div>
    </header>
  );
}
