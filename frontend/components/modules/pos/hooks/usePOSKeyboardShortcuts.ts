'use client';

import { useEffect, useCallback } from 'react';
import { usePOS } from '../context/POSContext';

/**
 * POS-specific keyboard shortcuts hook.
 * Registers F-key and other shortcuts for rapid POS operations.
 */
export function usePOSKeyboardShortcuts() {
  const { openModal, closeModal, cartItems, holdSale } = usePOS();

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Skip when typing in inputs
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') {
        // Allow F-keys even in inputs
        if (!e.key.startsWith('F')) return;
      }

      switch (e.key) {
        case 'F1': {
          e.preventDefault();
          openModal('keyboard_shortcuts');
          break;
        }
        case 'F2': {
          e.preventDefault();
          // Focus search bar
          const searchInput = document.querySelector<HTMLInputElement>('[data-pos-search]');
          searchInput?.focus();
          break;
        }
        case 'F3': {
          e.preventDefault();
          if (cartItems.length > 0) {
            openModal('payment');
          }
          break;
        }
        case 'F4': {
          e.preventDefault();
          if (cartItems.length > 0) {
            holdSale();
          }
          break;
        }
        case 'F5': {
          e.preventDefault();
          openModal('retrieve_hold');
          break;
        }
        case 'F12': {
          e.preventDefault();
          openModal('shift_close');
          break;
        }
        case 'Escape': {
          closeModal();
          break;
        }
      }
    },
    [openModal, closeModal, cartItems, holdSale]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
}
