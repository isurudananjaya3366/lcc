'use client';

import { Plus } from 'lucide-react';

interface AddNewAddressProps {
  onClick: () => void;
}

export const AddNewAddress = ({ onClick }: AddNewAddressProps) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full flex items-center gap-3 rounded-lg border-2 border-dashed border-gray-300 p-4 text-left transition-colors hover:border-gray-400 hover:bg-gray-50"
    >
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-100 text-gray-500">
        <Plus className="h-4 w-4" />
      </div>
      <span className="text-sm font-medium text-gray-700">Add New Address</span>
    </button>
  );
};
