'use client';

import Link from 'next/link';
import { ShoppingBag, FileText, MapPin } from 'lucide-react';

export const ContinueShopping = () => {
  return (
    <div className="flex flex-col items-center gap-3">
      <Link
        href="/"
        className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 transition-colors"
      >
        <ShoppingBag className="h-4 w-4" />
        Continue Shopping
      </Link>

      <div className="flex items-center gap-4">
        <Link
          href="#"
          className="inline-flex items-center gap-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
        >
          <FileText className="h-4 w-4" />
          View Order Details
        </Link>
        <span className="text-gray-300">|</span>
        <Link
          href="#"
          className="inline-flex items-center gap-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
        >
          <MapPin className="h-4 w-4" />
          Track Order
        </Link>
      </div>
    </div>
  );
};
