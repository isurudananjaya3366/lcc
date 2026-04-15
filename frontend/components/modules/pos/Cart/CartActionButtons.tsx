'use client';

import { PayButton } from './PayButton';
import { Button } from '@/components/ui/button';

interface CartActionButtonsProps {
  cartEmpty: boolean;
  grandTotal: number;
  onPay: () => void;
  onHold: () => void;
}

export function CartActionButtons({
  cartEmpty,
  grandTotal,
  onPay,
  onHold,
}: CartActionButtonsProps) {
  return (
    <div className="shrink-0 border-t border-gray-200 px-4 py-3 dark:border-gray-700">
      <div className="flex gap-2">
        <PayButton amount={grandTotal} disabled={cartEmpty} onClick={onPay} />
        <Button
          variant="outline"
          onClick={onHold}
          disabled={cartEmpty}
          className="px-4 py-2.5 text-sm font-medium"
        >
          Hold (F4)
        </Button>
      </div>
    </div>
  );
}
