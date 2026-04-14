'use client';

import { Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ImportButtonProps {
  onImport: () => void;
  disabled?: boolean;
}

export function ImportButton({ onImport, disabled }: ImportButtonProps) {
  return (
    <Button variant="outline" onClick={onImport} disabled={disabled}>
      <Upload className="mr-2 h-4 w-4" />
      Import
    </Button>
  );
}
