'use client';

import Image from 'next/image';
import { Star, Trash2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export interface ImageData {
  id: string;
  file: File;
  preview: string;
  isPrimary: boolean;
  order: number;
}

interface ImagePreviewGridProps {
  images: ImageData[];
  onDelete: (id: string) => void;
  onSetPrimary: (id: string) => void;
  disabled?: boolean;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function ImagePreviewGrid({
  images,
  onDelete,
  onSetPrimary,
  disabled = false,
}: ImagePreviewGridProps) {
  if (images.length === 0) {
    return <p className="py-6 text-center text-sm text-muted-foreground">No images uploaded yet</p>;
  }

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
      {images.map((img) => (
        <div
          key={img.id}
          className={cn(
            'group relative overflow-hidden rounded-lg border',
            img.isPrimary
              ? 'border-blue-500 ring-2 ring-blue-200 dark:ring-blue-800'
              : 'border-gray-200 dark:border-gray-700'
          )}
        >
          {/* Thumbnail */}
          <div className="relative aspect-square bg-gray-100 dark:bg-gray-800">
            <Image
              src={img.preview}
              alt={img.file.name}
              fill
              className="object-cover"
              sizes="(min-width: 1024px) 25vw, (min-width: 640px) 33vw, 50vw"
              unoptimized
            />

            {/* Primary Badge */}
            {img.isPrimary && (
              <Badge className="absolute left-1.5 top-1.5 gap-1 bg-blue-600 text-xs">
                <Star className="h-3 w-3" /> Primary
              </Badge>
            )}

            {/* Action Overlay */}
            <div className="absolute inset-0 flex items-center justify-center gap-2 bg-black/0 opacity-0 transition-all group-hover:bg-black/40 group-hover:opacity-100">
              {!img.isPrimary && (
                <Button
                  type="button"
                  variant="secondary"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => onSetPrimary(img.id)}
                  disabled={disabled}
                  title="Set as primary"
                >
                  <Star className="h-4 w-4" />
                </Button>
              )}
              <Button
                type="button"
                variant="destructive"
                size="icon"
                className="h-8 w-8"
                onClick={() => onDelete(img.id)}
                disabled={disabled}
                title="Delete image"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Metadata */}
          <div className="px-2 py-1.5">
            <p className="truncate text-xs text-gray-600 dark:text-gray-400">{img.file.name}</p>
            <p className="text-xs text-gray-400 dark:text-gray-500">{formatSize(img.file.size)}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
