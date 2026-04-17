'use client';

import { RemoveItemButton } from './RemoveItemButton';
import { SaveForLater } from './SaveForLater';

interface CartItemActionsProps {
  itemId: string;
  itemName: string;
  onRemove: () => void;
}

export function CartItemActions({ itemId: _itemId, itemName, onRemove }: CartItemActionsProps) {
  return (
    <div className="flex items-center gap-4">
      <RemoveItemButton onRemove={onRemove} itemName={itemName} />
      <SaveForLater />
    </div>
  );
}
