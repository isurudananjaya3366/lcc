'use client';

import { X } from 'lucide-react';

interface RemoveItemButtonProps {
  onRemove: () => void;
}

export function RemoveItemButton({ onRemove }: RemoveItemButtonProps) {
  return (
    <button
      onClick={onRemove}
      className="rounded p-1 text-gray-400 transition-colors hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-950"
      aria-label="Remove item"
    >
      <X className="h-3.5 w-3.5" />
    </button>
  );
}
