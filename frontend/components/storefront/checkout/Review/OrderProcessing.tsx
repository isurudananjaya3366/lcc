'use client';

import { Loader2 } from 'lucide-react';
import { useStoreCheckoutStore } from '@/stores/store';

export const OrderProcessing = () => {
  const isProcessing = useStoreCheckoutStore((s) => s.isProcessing);

  if (!isProcessing) return null;

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-4 rounded-xl bg-white p-10 shadow-2xl">
        <Loader2 className="h-12 w-12 animate-spin text-green-600" />
        <p className="text-lg font-semibold text-gray-900">Processing your order…</p>
        <p className="text-sm text-gray-500">Please wait, do not close this page.</p>
      </div>
    </div>
  );
};
