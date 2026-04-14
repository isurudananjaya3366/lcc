'use client';

import { useCallback, useRef } from 'react';

interface SwipeCallbacks {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
}

interface SwipeConfig {
  /** Minimum distance in px to be considered a swipe (default: 50). */
  threshold?: number;
  /** Minimum velocity in px/ms to be considered a swipe (default: 0.3). */
  velocityThreshold?: number;
  /** Maximum vertical distance — ignore diagonal moves (default: 100). */
  maxVertical?: number;
  /** For open-swipe: horizontal zone from left edge where swipe must start (default: 20). */
  edgeZone?: number;
  /** Require swipe-right to start from the left-edge zone (default: false). */
  edgeOnly?: boolean;
}

interface TouchState {
  startX: number;
  startY: number;
  startTime: number;
}

/**
 * Returns touch event handlers for detecting horizontal swipe gestures.
 *
 * Attach the returned `onTouchStart`, `onTouchMove`, and `onTouchEnd`
 * to the element you want to detect swipes on.
 */
export function useSwipeGesture(
  callbacks: SwipeCallbacks,
  config: SwipeConfig = {}
) {
  const {
    threshold = 50,
    velocityThreshold = 0.3,
    maxVertical = 100,
    edgeZone = 20,
    edgeOnly = false,
  } = config;

  const touchRef = useRef<TouchState | null>(null);

  const onTouchStart = useCallback(
    (e: React.TouchEvent | TouchEvent) => {
      const touch = e.touches[0];
      if (!touch) return;

      // If edgeOnly, only track touches starting in the left-edge zone
      if (edgeOnly && touch.clientX > edgeZone) return;

      touchRef.current = {
        startX: touch.clientX,
        startY: touch.clientY,
        startTime: Date.now(),
      };
    },
    [edgeOnly, edgeZone]
  );

  const onTouchMove = useCallback((_e: React.TouchEvent | TouchEvent) => {
    // Could add follow-finger visual feedback here in the future
  }, []);

  const onTouchEnd = useCallback(
    (e: React.TouchEvent | TouchEvent) => {
      if (!touchRef.current) return;

      const touch = e.changedTouches[0];
      if (!touch) return;

      const { startX, startY, startTime } = touchRef.current;
      touchRef.current = null;

      const deltaX = touch.clientX - startX;
      const deltaY = Math.abs(touch.clientY - startY);
      const elapsed = Date.now() - startTime;
      const velocity = Math.abs(deltaX) / elapsed;

      // Ignore vertical or too-small moves
      if (deltaY > maxVertical) return;
      if (Math.abs(deltaX) < threshold) return;
      if (velocity < velocityThreshold) return;

      if (deltaX > 0) {
        callbacks.onSwipeRight?.();
      } else {
        callbacks.onSwipeLeft?.();
      }
    },
    [callbacks, threshold, velocityThreshold, maxVertical]
  );

  return { onTouchStart, onTouchMove, onTouchEnd };
}
