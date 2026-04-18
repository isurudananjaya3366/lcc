'use client';

import { FileDown } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface DownloadInvoiceProps {
  orderId: string;
}

export function DownloadInvoice({ orderId }: DownloadInvoiceProps) {
  return (
    <Button variant="outline" disabled className="gap-2" title="Coming soon">
      <FileDown className="h-4 w-4" />
      Download Invoice
    </Button>
  );
}
