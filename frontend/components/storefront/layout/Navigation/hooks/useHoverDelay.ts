'use client';

import { useState, useRef, useEffect, useCallback } from 'react';

interface UseHoverDelayOptions {
  openDelay?: number;
  closeDelay?: number;
}

interface UseHoverDelayReturn {
  isHovered: boolean;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
}

export function useHoverDelay(options: UseHoverDelayOptions = {}): UseHoverDelayReturn {
  const { openDelay = 100, closeDelay = 200 } = options;
  const [isHovered, setIsHovered] = useState(false);
  const openTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const closeTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearTimers = useCallback(() => {
    if (openTimeout.current) {
      clearTimeout(openTimeout.current);
      openTimeout.current = null;
    }
    if (closeTimeout.current) {
      clearTimeout(closeTimeout.current);
      closeTimeout.current = null;
    }
  }, []);

  const onMouseEnter = useCallback(() => {
    if (closeTimeout.current) {
      clearTimeout(closeTimeout.current);
      closeTimeout.current = null;
    }
    openTimeout.current = setTimeout(() => {
      setIsHovered(true);
    }, openDelay);
  }, [openDelay]);

  const onMouseLeave = useCallback(() => {
    if (openTimeout.current) {
      clearTimeout(openTimeout.current);
      openTimeout.current = null;
    }
    closeTimeout.current = setTimeout(() => {
      setIsHovered(false);
    }, closeDelay);
  }, [closeDelay]);

  useEffect(() => {
    return clearTimers;
  }, [clearTimers]);

  return { isHovered, onMouseEnter, onMouseLeave };
}
