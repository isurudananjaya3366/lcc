'use client';

import { useState } from 'react';
import { Download, Loader2, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { invoiceService } from '@/services/api';

interface DownloadPDFButtonProps {
  invoiceId: string;
  invoiceNumber: string;
}

export function DownloadPDFButton({ invoiceId, invoiceNumber }: DownloadPDFButtonProps) {
  const [state, setState] = useState<'idle' | 'loading' | 'success'>('idle');

  const handleDownload = async () => {
    setState('loading');
    try {
      const blob = await invoiceService.downloadInvoicePdf(invoiceId);
      const url = URL.createObjectURL(blob as unknown as Blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Invoice-${invoiceNumber}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setState('success');
      setTimeout(() => setState('idle'), 2000);
    } catch {
      setState('idle');
    }
  };

  return (
    <Button variant="outline" size="sm" onClick={handleDownload} disabled={state === 'loading'}>
      {state === 'loading' ? (
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      ) : state === 'success' ? (
        <CheckCircle className="mr-2 h-4 w-4 text-green-600" />
      ) : (
        <Download className="mr-2 h-4 w-4" />
      )}
      {state === 'success' ? 'Downloaded' : 'Download PDF'}
    </Button>
  );
}
