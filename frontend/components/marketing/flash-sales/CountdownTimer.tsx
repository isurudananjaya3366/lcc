'use client';

import { Timer } from 'lucide-react';
import { useCountdown } from '@/hooks/marketing/useCountdown';

interface CountdownTimerProps {
  endDate: string;
  label?: string;
  variant?: 'default' | 'compact' | 'hero';
  onExpired?: () => void;
  className?: string;
}

function TimeUnit({ value, label }: { value: number; label: string }) {
  return (
    <div className="flex flex-col items-center">
      <span className="rounded bg-gray-900 px-2 py-1 font-mono text-lg font-bold text-white tabular-nums">
        {String(value).padStart(2, '0')}
      </span>
      <span className="mt-0.5 text-[10px] uppercase text-gray-500">{label}</span>
    </div>
  );
}

export function CountdownTimer({ endDate, label, variant = 'default', onExpired, className = '' }: CountdownTimerProps) {
  const { days, hours, minutes, seconds, isExpired, formatTime } = useCountdown(endDate, onExpired);

  if (isExpired) {
    return (
      <div className={`text-center text-sm font-medium text-red-500 ${className}`}>Sale Ended</div>
    );
  }

  if (variant === 'compact') {
    return (
      <div className={`inline-flex items-center gap-1 text-sm font-medium text-red-600 ${className}`}>
        <Timer className="h-3.5 w-3.5" />
        <span className="font-mono tabular-nums">{formatTime()}</span>
      </div>
    );
  }

  return (
    <div className={className}>
      {label && (
        <div className="mb-2 flex items-center justify-center gap-1.5 text-sm font-medium text-red-600">
          <Timer className="h-4 w-4" />
          {label}
        </div>
      )}
      <div className="flex items-center justify-center gap-2">
        {days > 0 && <TimeUnit value={days} label="Days" />}
        <TimeUnit value={hours} label="Hrs" />
        <span className="text-xl font-bold text-gray-400">:</span>
        <TimeUnit value={minutes} label="Min" />
        <span className="text-xl font-bold text-gray-400">:</span>
        <TimeUnit value={seconds} label="Sec" />
      </div>
    </div>
  );
}
