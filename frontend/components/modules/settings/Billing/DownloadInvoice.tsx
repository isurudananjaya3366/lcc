'use client';

import { Download, Loader2 } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';

interface DownloadInvoiceProps {
  invoiceId: string;
  invoiceNumber: string;
}

export function DownloadInvoice({ invoiceId, invoiceNumber }: DownloadInvoiceProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleDownload = async () => {
    setIsLoading(true);
    try {
      // In production, this would fetch from the API
      // const response = await fetch(`/api/billing/invoices/${invoiceId}/download`);
      // const blob = await response.blob();
      // const url = window.URL.createObjectURL(blob);
      // const a = document.createElement('a');
      // a.href = url;
      // a.download = `invoice-${invoiceNumber}.pdf`;
      // a.click();
      // window.URL.revokeObjectURL(url);

      // Mock download simulation
      await new Promise((resolve) => setTimeout(resolve, 1000));
      console.log(`Downloading invoice ${invoiceNumber} (${invoiceId})`);
    } catch {
      console.error('Failed to download invoice');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={handleDownload}
      disabled={isLoading}
      title={`Download ${invoiceNumber}`}
    >
      {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
    </Button>
  );
}
