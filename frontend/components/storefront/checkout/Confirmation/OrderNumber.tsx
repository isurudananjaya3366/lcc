'use client';

import { useState } from 'react';
import { Copy, Check } from 'lucide-react';

interface OrderNumberProps {
  orderNumber: string;
}

export const OrderNumber = ({ orderNumber }: OrderNumberProps) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(orderNumber);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard not available
    }
  };

  return (
    <div className="inline-flex items-center gap-3 rounded-lg bg-green-50 px-5 py-3 border border-green-200">
      <div className="text-center">
        <p className="text-xs font-medium text-green-700 uppercase tracking-wider">Order Number</p>
        <p className="mt-1 text-lg font-bold text-green-900 tracking-wide">{orderNumber}</p>
      </div>
      <button
        type="button"
        onClick={handleCopy}
        className="rounded-md p-1.5 text-green-600 hover:bg-green-100 transition-colors"
        aria-label="Copy order number"
      >
        {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
      </button>
    </div>
  );
};
