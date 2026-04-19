'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

interface UseExitIntentOptions {
  threshold?: number;
  delay?: number;
  onTrigger?: () => void;
}

export function useExitIntent({ threshold = 10, delay = 0, onTrigger }: UseExitIntentOptions = {}) {
  const [triggered, setTriggered] = useState(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const firedRef = useRef(false);

  const handleMouseLeave = useCallback(
    (e: MouseEvent) => {
      if (firedRef.current) return;
      if (e.clientY > threshold) return;

      const fire = () => {
        firedRef.current = true;
        setTriggered(true);
        onTrigger?.();
      };

      if (delay > 0) {
        timeoutRef.current = setTimeout(fire, delay);
      } else {
        fire();
      }
    },
    [threshold, delay, onTrigger]
  );

  const handleMouseEnter = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  useEffect(() => {
    document.addEventListener('mouseleave', handleMouseLeave);
    document.addEventListener('mouseenter', handleMouseEnter);
    return () => {
      document.removeEventListener('mouseleave', handleMouseLeave);
      document.removeEventListener('mouseenter', handleMouseEnter);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [handleMouseLeave, handleMouseEnter]);

  const reset = useCallback(() => {
    firedRef.current = false;
    setTriggered(false);
  }, []);

  return { triggered, reset };
}
