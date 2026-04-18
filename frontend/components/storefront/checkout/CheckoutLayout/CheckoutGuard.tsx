'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useStoreCartStore } from '@/stores/store';

interface CheckoutGuardProps {
  children: React.ReactNode;
}

export const CheckoutGuard = ({ children }: CheckoutGuardProps) => {
  const router = useRouter();
  const itemCount = useStoreCartStore((s) => s.getItemCount());

  useEffect(() => {
    if (itemCount === 0) {
      router.replace('/cart');
    }
  }, [itemCount, router]);

  if (itemCount === 0) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <p className="text-gray-500">Redirecting to cart...</p>
      </div>
    );
  }

  return <>{children}</>;
};
