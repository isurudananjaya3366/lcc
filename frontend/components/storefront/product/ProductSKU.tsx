'use client';

import { useState, useCallback } from 'react';
import { toast } from 'sonner';

interface ProductSKUProps {
  sku: string;
}

export function ProductSKU({ sku }: ProductSKUProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(sku);
      setCopied(true);
      toast.success('SKU copied!', { duration: 2000 });
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error('Failed to copy SKU');
    }
  }, [sku]);

  return (
    <div className="flex items-center gap-2 text-sm text-gray-500">
      <span>
        SKU: <span className="font-mono font-medium text-gray-700">{sku}</span>
      </span>
      <button
        onClick={handleCopy}
        aria-label="Copy SKU to clipboard"
        className="rounded p-0.5 text-gray-400 hover:text-gray-600 transition-colors"
        title="Copy SKU"
      >
        {copied ? (
          <svg className="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
        ) : (
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1 1.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0 0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 0 1-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H9.75" />
          </svg>
        )}
      </button>
    </div>
  );
}
