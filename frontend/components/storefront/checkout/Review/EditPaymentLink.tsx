'use client';

import { useRouter } from 'next/navigation';
import { Pencil } from 'lucide-react';

export const EditPaymentLink = () => {
  const router = useRouter();

  return (
    <button
      type="button"
      onClick={() => router.push('/checkout/payment')}
      className="inline-flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
    >
      <Pencil className="h-3.5 w-3.5" />
      Edit
    </button>
  );
};
