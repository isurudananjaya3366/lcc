'use client';

import { useState, useCallback } from 'react';
import { type Control, type UseFormSetValue, type UseFormWatch } from 'react-hook-form';
import type { ProductFormData } from '@/lib/validations/product';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ImageUploadZone } from './ImageUploadZone';
import { ImagePreviewGrid, type ImageData } from './ImagePreviewGrid';

interface MediaSectionProps {
  control: Control<ProductFormData>;
  setValue: UseFormSetValue<ProductFormData>;
  isLoading?: boolean;
  watch: UseFormWatch<ProductFormData>;
}

export function MediaSection({ setValue, isLoading = false, watch }: MediaSectionProps) {
  const [images, setImages] = useState<ImageData[]>([]);

  const syncFormValue = useCallback(
    (updated: ImageData[]) => {
      setImages(updated);
      setValue(
        'images',
        updated.map((img) => img.file),
        { shouldValidate: true }
      );
    },
    [setValue]
  );

  const handleUpload = useCallback(
    (files: File[]) => {
      const newImages: ImageData[] = files.map((file, i) => ({
        id: crypto.randomUUID(),
        file,
        preview: URL.createObjectURL(file),
        isPrimary: images.length === 0 && i === 0,
        order: images.length + i,
      }));

      syncFormValue([...images, ...newImages]);
    },
    [images, syncFormValue]
  );

  const handleDelete = useCallback(
    (id: string) => {
      const updated = images.filter((img) => img.id !== id);
      // If we removed the primary, promote the first remaining
      if (updated.length > 0 && !updated.some((img) => img.isPrimary)) {
        updated[0].isPrimary = true;
      }
      // Reindex order
      updated.forEach((img, i) => {
        img.order = i;
      });
      syncFormValue(updated);
    },
    [images, syncFormValue]
  );

  const handleSetPrimary = useCallback(
    (id: string) => {
      const updated = images.map((img) => ({
        ...img,
        isPrimary: img.id === id,
      }));
      syncFormValue(updated);
    },
    [images, syncFormValue]
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Product Images</CardTitle>
        <CardDescription>
          Upload images for this product (max 10, 5MB each, JPEG/PNG/WebP)
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <ImageUploadZone
          onUpload={handleUpload}
          currentCount={images.length}
          disabled={isLoading}
        />

        {images.length > 0 && (
          <ImagePreviewGrid
            images={images}
            onDelete={handleDelete}
            onSetPrimary={handleSetPrimary}
            disabled={isLoading}
          />
        )}
      </CardContent>
    </Card>
  );
}
