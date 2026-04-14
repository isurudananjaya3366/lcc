'use client';

import { useEffect, useMemo, useState } from 'react';
import type { KeyboardShortcut } from '@/hooks/useKeyboardShortcuts';
import { cn } from '@/lib/cn';

interface ShortcutsModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  shortcuts?: KeyboardShortcut[];
}

export function ShortcutsModal({ open, onOpenChange, shortcuts = [] }: ShortcutsModalProps) {
  const [isMac, setIsMac] = useState(false);

  useEffect(() => {
    setIsMac(navigator.platform.toUpperCase().includes('MAC'));
  }, []);

  // close on Escape
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onOpenChange(false);
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [open, onOpenChange]);

  const grouped = useMemo(() => {
    const map = new Map<string, KeyboardShortcut[]>();
    for (const s of shortcuts) {
      const list = map.get(s.category) ?? [];
      list.push(s);
      map.set(s.category, list);
    }
    return map;
  }, [shortcuts]);

  if (!open) return null;

  const modLabel = isMac ? '⌘' : 'Ctrl';

  return (
    <div
      className="fixed inset-0 z-50"
      role="dialog"
      aria-modal="true"
      aria-label="Keyboard shortcuts"
    >
      <div
        className="fixed inset-0 bg-black/50 animate-in fade-in-0"
        onClick={() => onOpenChange(false)}
        aria-hidden="true"
      />

      <div className="fixed left-1/2 top-1/2 w-full max-w-lg -translate-x-1/2 -translate-y-1/2 rounded-xl border bg-white p-6 shadow-2xl dark:border-gray-700 dark:bg-gray-800">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-foreground">Keyboard Shortcuts</h2>
          <button
            type="button"
            onClick={() => onOpenChange(false)}
            className="rounded-md p-1 text-muted-foreground hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        <div className="max-h-[60vh] space-y-6 overflow-y-auto">
          {Array.from(grouped.entries()).map(([category, items]) => (
            <div key={category}>
              <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                {category}
              </h3>
              <ul className="space-y-1">
                {items.map((s) => (
                  <li
                    key={s.description}
                    className="flex items-center justify-between rounded-md px-2 py-1.5 text-sm hover:bg-muted/50"
                  >
                    <span className="text-foreground">{s.description}</span>
                    <KeyCombo shortcut={s} modLabel={modLabel} />
                  </li>
                ))}
              </ul>
            </div>
          ))}

          {grouped.size === 0 && (
            <p className="py-4 text-center text-sm text-muted-foreground">
              No shortcuts registered.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function KeyCombo({ shortcut, modLabel }: { shortcut: KeyboardShortcut; modLabel: string }) {
  const parts: string[] = [];
  if (shortcut.metaKey || shortcut.ctrlKey) parts.push(modLabel);
  if (shortcut.shiftKey) parts.push('Shift');
  if (shortcut.altKey) parts.push('Alt');
  parts.push(shortcut.key.toUpperCase());

  return (
    <div className="flex gap-1">
      {parts.map((p) => (
        <kbd
          key={p}
          className={cn(
            'rounded border border-border bg-muted px-1.5 py-0.5 text-[11px] font-medium text-muted-foreground'
          )}
        >
          {p}
        </kbd>
      ))}
    </div>
  );
}
