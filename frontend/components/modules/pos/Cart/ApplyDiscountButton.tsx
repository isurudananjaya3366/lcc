'use client';

import { Percent } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useCartStore } from '@/stores/pos/cart';

interface ApplyDiscountButtonProps {
  onClick: () => void;
}

export function ApplyDiscountButton({ onClick }: ApplyDiscountButtonProps) {
  const isEmpty = useCartStore().getItemCount() === 0;

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={onClick}
      disabled={isEmpty}
      className="h-6 gap-1 px-2 text-xs text-gray-500 hover:text-green-600"
      title="Apply discount ( / )"
    >
      <Percent className="h-3 w-3" />
      Discount
    </Button>
  );
}
