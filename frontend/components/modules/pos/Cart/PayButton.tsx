'use client';

import { Button } from '@/components/ui/button';

interface PayButtonProps {
  amount: number;
  disabled: boolean;
  onClick: () => void;
}

export function PayButton({ amount, disabled, onClick }: PayButtonProps) {
  return (
    <Button
      onClick={onClick}
      disabled={disabled}
      className="flex-1 py-2.5 text-sm font-semibold"
      size="lg"
    >
      Pay ₨ {amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })} (F3)
    </Button>
  );
}
