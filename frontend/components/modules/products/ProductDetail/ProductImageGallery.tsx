'use client';

import { useState, useCallback } from 'react';
import Image from 'next/image';
import type { ProductImage } from '@/types/product';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ProductImageGalleryProps {
  images: ProductImage[];
}

export function ProductImageGallery({ images }: ProductImageGalleryProps) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [lightboxOpen, setLightboxOpen] = useState(false);

  const sortedImages = [...images].sort((a, b) => {
    if (a.isPrimary) return -1;
    if (b.isPrimary) return 1;
    return a.position - b.position;
  });

  const currentImage = sortedImages[selectedIndex];

  const goToPrevious = useCallback(() => {
    setSelectedIndex((prev) => (prev > 0 ? prev - 1 : sortedImages.length - 1));
  }, [sortedImages.length]);

  const goToNext = useCallback(() => {
    setSelectedIndex((prev) => (prev < sortedImages.length - 1 ? prev + 1 : 0));
  }, [sortedImages.length]);

  if (sortedImages.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Images</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex h-48 items-center justify-center rounded-md border border-dashed dark:border-gray-700">
            <p className="text-sm text-gray-500 dark:text-gray-400">No images uploaded</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Images</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {/* Main Image */}
          <button
            type="button"
            className="relative w-full aspect-square rounded-md overflow-hidden border dark:border-gray-700 cursor-pointer"
            onClick={() => setLightboxOpen(true)}
          >
            <Image
              src={currentImage.url}
              alt={currentImage.alt}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, 400px"
            />
            {currentImage.isPrimary && (
              <Badge className="absolute top-2 left-2" variant="default">
                Primary
              </Badge>
            )}
          </button>

          {/* Thumbnails */}
          {sortedImages.length > 1 && (
            <div className="grid grid-cols-4 gap-2">
              {sortedImages.map((img, idx) => (
                <button
                  key={img.id}
                  type="button"
                  className={cn(
                    'relative aspect-square rounded-md overflow-hidden border transition-colors',
                    idx === selectedIndex
                      ? 'border-primary ring-2 ring-primary/30'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-400'
                  )}
                  onClick={() => setSelectedIndex(idx)}
                >
                  <Image
                    src={img.thumbnailUrl || img.url}
                    alt={img.alt}
                    fill
                    className="object-cover"
                    sizes="100px"
                  />
                </button>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Lightbox */}
      <Dialog open={lightboxOpen} onOpenChange={setLightboxOpen}>
        <DialogContent className="max-w-4xl p-0 bg-black/95 border-none">
          <div className="relative flex items-center justify-center min-h-[60vh]">
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-2 right-2 z-10 text-white hover:bg-white/20"
              onClick={() => setLightboxOpen(false)}
            >
              <X className="h-5 w-5" />
            </Button>

            {sortedImages.length > 1 && (
              <>
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute left-2 z-10 text-white hover:bg-white/20"
                  onClick={goToPrevious}
                >
                  <ChevronLeft className="h-6 w-6" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute right-2 z-10 text-white hover:bg-white/20"
                  onClick={goToNext}
                >
                  <ChevronRight className="h-6 w-6" />
                </Button>
              </>
            )}

            <div className="relative w-full aspect-video">
              <Image
                src={currentImage.url}
                alt={currentImage.alt}
                fill
                className="object-contain"
                sizes="(max-width: 768px) 100vw, 900px"
              />
            </div>

            {sortedImages.length > 1 && (
              <div className="absolute bottom-4 left-0 right-0 text-center text-white/70 text-sm">
                {selectedIndex + 1} / {sortedImages.length}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
