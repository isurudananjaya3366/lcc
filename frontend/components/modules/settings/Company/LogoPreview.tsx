'use client';

import Image from 'next/image';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface LogoPreviewProps {
  src: string;
  alt?: string;
  onRemove: () => void;
}

export function LogoPreview({ src, alt = 'Company logo', onRemove }: LogoPreviewProps) {
  return (
    <div className="group relative inline-block">
      <div className="h-24 w-24 overflow-hidden rounded-lg border shadow-sm">
        <Image
          src={src}
          alt={alt}
          width={96}
          height={96}
          className="h-full w-full object-contain"
          unoptimized
        />
      </div>
      <Button
        type="button"
        variant="destructive"
        size="icon"
        className="absolute -right-2 -top-2 h-6 w-6 opacity-0 transition-opacity group-hover:opacity-100"
        onClick={onRemove}
      >
        <X className="h-3 w-3" />
      </Button>
    </div>
  );
}
