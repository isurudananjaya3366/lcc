'use client';

import { useCallback, useEffect, useRef } from 'react';

/**
 * React hook for managing request cancellation with AbortController.
 *
 * Automatically aborts in-flight requests on component unmount.
 * Provides a `getSignal()` method to obtain a fresh AbortSignal
 * that cancels the previous request if one is still active.
 *
 * @example
 * ```tsx
 * function ProductList() {
 *   const { getSignal, abort, isAborted } = useAbortController();
 *
 *   const fetchProducts = async () => {
 *     const signal = getSignal();
 *     const res = await apiClient.get('/products', { signal });
 *     // ...
 *   };
 *
 *   return <button onClick={abort}>Cancel</button>;
 * }
 * ```
 */
export function useAbortController() {
  const controllerRef = useRef<AbortController | null>(null);

  // Abort any active request and return a new signal
  const getSignal = useCallback((): AbortSignal => {
    // Cancel previous in-flight request
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    return controller.signal;
  }, []);

  // Manually abort current request
  const abort = useCallback(() => {
    controllerRef.current?.abort();
    controllerRef.current = null;
  }, []);

  // Check if current controller is aborted
  const isAborted = useCallback((): boolean => {
    return controllerRef.current?.signal.aborted ?? false;
  }, []);

  // Auto-abort on unmount
  useEffect(() => {
    return () => {
      controllerRef.current?.abort();
    };
  }, []);

  return { getSignal, abort, isAborted };
}
