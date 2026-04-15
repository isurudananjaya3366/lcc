'use client';

import { useEffect, useRef } from 'react';
import { RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface NewSaleButtonProps {
  onNewSale: () => void;
}

export function NewSaleButton({ onNewSale }: NewSaleButtonProps) {
  const btnRef = useRef<HTMLButtonElement>(null);

  // Auto-focus after 2 seconds
  useEffect(() => {
    const timer = setTimeout(() => btnRef.current?.focus(), 2000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <Button ref={btnRef} size="sm" onClick={onNewSale} className="flex-1">
      <RotateCcw className="mr-1.5 h-4 w-4" />
      New Sale (N)
    </Button>
  );
}
