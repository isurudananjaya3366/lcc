'use client';

import { useCallback, useEffect, useRef } from 'react';

export interface KeyboardShortcut {
  key: string;
  metaKey?: boolean;
  ctrlKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  description: string;
  action: () => void;
  category: string;
}

function buildCombination(e: KeyboardEvent): string {
  const parts: string[] = [];
  if (e.metaKey || e.ctrlKey) parts.push('mod');
  if (e.shiftKey) parts.push('shift');
  if (e.altKey) parts.push('alt');
  parts.push(e.key.toLowerCase());
  return parts.join('+');
}

function shortcutToCombination(s: KeyboardShortcut): string {
  const parts: string[] = [];
  if (s.metaKey || s.ctrlKey) parts.push('mod');
  if (s.shiftKey) parts.push('shift');
  if (s.altKey) parts.push('alt');
  parts.push(s.key.toLowerCase());
  return parts.join('+');
}

function isInputFocused(): boolean {
  const el = document.activeElement;
  if (!el) return false;
  const tag = el.tagName;
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return true;
  if ((el as HTMLElement).isContentEditable) return true;
  return false;
}

/**
 * Register keyboard shortcuts and listen for them globally.
 * Returns the list of registered shortcuts (for the help modal).
 */
export function useKeyboardShortcuts(shortcuts: KeyboardShortcut[]) {
  const registryRef = useRef(new Map<string, KeyboardShortcut>());

  // Rebuild registry when shortcuts change
  useEffect(() => {
    const map = new Map<string, KeyboardShortcut>();
    for (const s of shortcuts) {
      map.set(shortcutToCombination(s), s);
    }
    registryRef.current = map;
  }, [shortcuts]);

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    // Allow Escape always
    if (e.key === 'Escape') {
      const entry = registryRef.current.get('escape');
      if (entry) {
        e.preventDefault();
        entry.action();
      }
      return;
    }

    // Skip if user is typing in a form field (unless mod key is held)
    if (isInputFocused() && !(e.metaKey || e.ctrlKey)) return;

    const combo = buildCombination(e);
    const entry = registryRef.current.get(combo);
    if (entry) {
      e.preventDefault();
      entry.action();
    }
  }, []);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return { shortcuts };
}
