'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import type { CountdownTime } from '@/types/marketing/flash-sale.types';

function calculateTimeRemaining(endDate: string): CountdownTime {
  const diff = new Date(endDate).getTime() - Date.now();

  if (diff <= 0) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0, isExpired: true, totalSeconds: 0 };
  }

  const totalSeconds = Math.floor(diff / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  return { days, hours, minutes, seconds, isExpired: false, totalSeconds };
}

export function useCountdown(endDate: string, onExpired?: () => void) {
  const [time, setTime] = useState<CountdownTime>(() => calculateTimeRemaining(endDate));
  const onExpiredRef = useRef(onExpired);
  onExpiredRef.current = onExpired;

  useEffect(() => {
    const interval = setInterval(() => {
      const remaining = calculateTimeRemaining(endDate);
      setTime(remaining);
      if (remaining.isExpired) {
        clearInterval(interval);
        onExpiredRef.current?.();
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [endDate]);

  const formatTime = useCallback(() => {
    if (time.isExpired) return 'Ended';
    if (time.days > 0) return `${time.days}d ${time.hours}h ${time.minutes}m`;
    if (time.hours > 0) return `${time.hours}h ${time.minutes}m ${time.seconds}s`;
    return `${time.minutes}m ${time.seconds}s`;
  }, [time]);

  return { ...time, formatTime };
}
