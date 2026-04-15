'use client';

import { MoreVertical, Percent, XCircle, StickyNote, Eye } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface ItemOptionsMenuProps {
  hasDiscount: boolean;
  onApplyDiscount: () => void;
  onRemoveDiscount: () => void;
}

export function ItemOptionsMenu({
  hasDiscount,
  onApplyDiscount,
  onRemoveDiscount,
}: ItemOptionsMenuProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          className="rounded p-1 text-gray-400 transition-colors hover:bg-gray-200 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-300"
          aria-label="Item options"
        >
          <MoreVertical className="h-3.5 w-3.5" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-40">
        {hasDiscount ? (
          <DropdownMenuItem onClick={onRemoveDiscount}>
            <XCircle className="mr-2 h-4 w-4" />
            Remove Discount
          </DropdownMenuItem>
        ) : (
          <DropdownMenuItem onClick={onApplyDiscount}>
            <Percent className="mr-2 h-4 w-4" />
            Apply Discount
          </DropdownMenuItem>
        )}
        <DropdownMenuSeparator />
        <DropdownMenuItem disabled>
          <StickyNote className="mr-2 h-4 w-4" />
          Add Note
        </DropdownMenuItem>
        <DropdownMenuItem disabled>
          <Eye className="mr-2 h-4 w-4" />
          View Details
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
