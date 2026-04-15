'use client';

import Image from 'next/image';
import { Eye, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface LogoPreviewProps {
  src: string;
  alt?: string;
  onRemove: () => void;
}

export function LogoPreview({ src, alt = 'Company logo', onRemove }: LogoPreviewProps) {
  const handleView = () => {
    window.open(src, '_blank', 'noopener,noreferrer');
  };

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
      <div className="absolute -right-2 -top-2 flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
        <Button
          type="button"
          variant="secondary"
          size="icon"
          className="h-6 w-6"
          onClick={handleView}
          title="View full size"
        >
          <Eye className="h-3 w-3" />
        </Button>
        <Button
          type="button"
          variant="destructive"
          size="icon"
          className="h-6 w-6"
          onClick={onRemove}
          title="Remove logo"
        >
          <X className="h-3 w-3" />
        </Button>
      </div>
    </div>
  );
}
