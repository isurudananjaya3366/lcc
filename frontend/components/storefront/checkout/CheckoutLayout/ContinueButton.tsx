'use client';

import { Loader2 } from 'lucide-react';
import { useCheckoutNavigation } from '@/hooks/storefront/useCheckoutNavigation';

interface ContinueButtonProps {
  onClick?: () => Promise<boolean> | boolean;
  disabled?: boolean;
  loading?: boolean;
  label?: string;
}

export const ContinueButton = ({
  onClick,
  disabled = false,
  loading = false,
  label = 'Continue',
}: ContinueButtonProps) => {
  const { goToNext, canProceed } = useCheckoutNavigation();

  const handleClick = async () => {
    if (onClick) {
      const isValid = await onClick();
      if (!isValid) return;
    }
    goToNext();
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled || loading || !canProceed}
      className="inline-flex items-center justify-center gap-2 px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
    >
      {loading && <Loader2 className="w-4 h-4 animate-spin" />}
      {label}
    </button>
  );
};
