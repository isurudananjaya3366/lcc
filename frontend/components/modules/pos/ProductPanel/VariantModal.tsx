'use client';

import { useState } from 'react';
import { X, Minus, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ProductImage } from './ProductImage';
import { PriceDisplay } from './PriceDisplay';
import { StockIndicator } from './StockIndicator';
import type { ProductSearchResult, ProductVariant } from '../types';
import { usePOS } from '../context/POSContext';

interface VariantModalProps {
  product: ProductSearchResult | null;
  open: boolean;
  onClose: () => void;
}

export function VariantModal({ product, open, onClose }: VariantModalProps) {
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null);
  const [quantity, setQuantity] = useState(1);
  const { addToCart } = usePOS();

  if (!product) return null;

  const variants = product.variants ?? [];

  const handleAdd = () => {
    if (!selectedVariant) return;
    addToCart({
      productId: product.id,
      productName: product.name,
      sku: selectedVariant.sku,
      variantId: selectedVariant.id,
      variantName: selectedVariant.name,
      unitPrice: selectedVariant.price,
      originalPrice: selectedVariant.price,
      quantity,
      taxRate: 0,
      isTaxable: true,
      imageUrl: product.imageUrl,
    });
    onClose();
    setSelectedVariant(null);
    setQuantity(1);
  };

  const canAdd = selectedVariant && selectedVariant.stockQuantity > 0 && quantity > 0;

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <ProductImage src={product.imageUrl} alt={product.name} size="sm" />
            <div>
              <span>{product.name}</span>
              <PriceDisplay price={product.price} size="sm" showFrom />
            </div>
          </DialogTitle>
        </DialogHeader>

        {/* Variant Selection */}
        <div className="max-h-48 space-y-2 overflow-y-auto">
          {variants.map((variant) => {
            const isOos = variant.stockQuantity <= 0;
            const isSelected = selectedVariant?.id === variant.id;
            return (
              <button
                key={variant.id}
                onClick={() => !isOos && setSelectedVariant(variant)}
                disabled={isOos}
                className={`flex w-full items-center justify-between rounded-md border px-3 py-2 text-left text-sm transition-colors ${
                  isSelected
                    ? 'border-primary bg-primary/5'
                    : isOos
                      ? 'cursor-not-allowed border-gray-200 opacity-50 dark:border-gray-700'
                      : 'border-gray-200 hover:border-gray-300 dark:border-gray-700'
                }`}
              >
                <div>
                  <span className="font-medium">{variant.name}</span>
                  <div className="mt-0.5 flex items-center gap-2">
                    <span className="text-xs text-gray-500">{variant.sku}</span>
                    <StockIndicator quantity={variant.stockQuantity} variant="dot" />
                  </div>
                </div>
                <PriceDisplay price={variant.price} size="sm" />
              </button>
            );
          })}
        </div>

        {/* Quantity Selector */}
        <div className="flex items-center justify-between border-t pt-3 dark:border-gray-700">
          <span className="text-sm font-medium">Quantity</span>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8"
              onClick={() => setQuantity((q) => Math.max(1, q - 1))}
              disabled={quantity <= 1}
            >
              <Minus className="h-3 w-3" />
            </Button>
            <input
              type="number"
              value={quantity}
              onChange={(e) => {
                const val = parseInt(e.target.value, 10);
                if (!isNaN(val) && val > 0) setQuantity(val);
              }}
              className="h-8 w-14 rounded border border-gray-300 text-center text-sm dark:border-gray-600 dark:bg-gray-800"
              min={1}
              max={selectedVariant?.stockQuantity || 9999}
            />
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8"
              onClick={() => setQuantity((q) => q + 1)}
              disabled={selectedVariant ? quantity >= selectedVariant.stockQuantity : false}
            >
              <Plus className="h-3 w-3" />
            </Button>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Button variant="outline" className="flex-1" onClick={onClose}>
            Cancel
          </Button>
          <Button className="flex-1" onClick={handleAdd} disabled={!canAdd}>
            Add to Cart
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
