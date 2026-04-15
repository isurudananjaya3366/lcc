'use client';

import type { ReactNode } from 'react';

interface POSMainContainerProps {
  productPanel: ReactNode;
  cartPanel: ReactNode;
}

export function POSMainContainer({ productPanel, cartPanel }: POSMainContainerProps) {
  return (
    <div className="flex min-h-0 flex-1 gap-4 p-4">
      {/* Product Panel - Left (65%) */}
      <div className="hidden w-full flex-col overflow-hidden rounded-lg border border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900 md:flex md:w-[65%] lg:w-[65%]">
        {productPanel}
      </div>

      {/* Cart Panel - Right (35%) */}
      <div className="flex w-full flex-col overflow-hidden rounded-lg border border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900 md:w-[35%] lg:w-[35%]">
        {cartPanel}
      </div>

      {/* Mobile: Product Panel shows above cart via tabs — handled within panels */}
    </div>
  );
}
