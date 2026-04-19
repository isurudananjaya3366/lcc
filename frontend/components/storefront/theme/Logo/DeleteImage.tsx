'use client';

import { useState } from 'react';
import { Trash2 } from 'lucide-react';

export interface DeleteImageProps {
  onDelete: () => void;
  label?: string;
  disabled?: boolean;
}

export function DeleteImage({
  onDelete,
  label = 'Remove Image',
  disabled = false,
}: DeleteImageProps) {
  const [confirming, setConfirming] = useState(false);

  const handleClick = () => {
    if (confirming) {
      onDelete();
      setConfirming(false);
    } else {
      setConfirming(true);
    }
  };

  const handleCancel = () => {
    setConfirming(false);
  };

  return (
    <div className="inline-flex items-center gap-2">
      <button
        type="button"
        onClick={handleClick}
        disabled={disabled}
        className={`inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors disabled:opacity-50 ${
          confirming
            ? 'bg-red-600 text-white hover:bg-red-700'
            : 'border border-red-300 text-red-600 hover:bg-red-50'
        }`}
      >
        <Trash2 className="h-4 w-4" />
        {confirming ? 'Confirm Delete' : label}
      </button>
      {confirming && (
        <button
          type="button"
          onClick={handleCancel}
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50"
        >
          Cancel
        </button>
      )}
    </div>
  );
}
