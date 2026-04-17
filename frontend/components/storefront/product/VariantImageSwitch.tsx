'use client';

import { useEffect, useRef } from 'react';
import type { ProductVariant } from '@/lib/api/store/modules/products';

interface VariantImageMapping {
  variantId: number;
  imageIndex: number;
}

interface VariantImageSwitchProps {
  variants: ProductVariant[];
  currentVariant: number | null;
  imageMappings: VariantImageMapping[];
  onImageSwitch: (imageIndex: number) => void;
}

export function VariantImageSwitch({
  currentVariant,
  imageMappings,
  onImageSwitch,
}: VariantImageSwitchProps) {
  const prevVariantRef = useRef<number | null>(currentVariant);

  useEffect(() => {
    if (currentVariant === null || currentVariant === prevVariantRef.current) return;

    prevVariantRef.current = currentVariant;

    const mapping = imageMappings.find((m) => m.variantId === currentVariant);
    if (mapping !== undefined) {
      onImageSwitch(mapping.imageIndex);
    }
  }, [currentVariant, imageMappings, onImageSwitch]);

  // This component has no visual output — it's a behavior-only connector
  return null;
}
