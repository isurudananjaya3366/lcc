'use client';

import { ArrowLeft } from 'lucide-react';
import { useCheckoutNavigation } from '@/hooks/storefront/useCheckoutNavigation';

export const BackButton = () => {
  const { goToPrevious, canGoBack } = useCheckoutNavigation();

  if (!canGoBack) return null;

  return (
    <button
      type="button"
      onClick={goToPrevious}
      className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
    >
      <ArrowLeft className="w-4 h-4" />
      Back
    </button>
  );
};
