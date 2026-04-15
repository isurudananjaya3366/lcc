'use client';

import { Printer } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function PrintReceiptButton() {
  return (
    <Button variant="outline" size="sm" onClick={() => window.print()} className="flex-1">
      <Printer className="mr-1.5 h-4 w-4" />
      Print (P)
    </Button>
  );
}
