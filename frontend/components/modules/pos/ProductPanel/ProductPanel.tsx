'use client';

import { useState } from 'react';
import { ProductSearch } from './ProductSearch';
import { QuickButtons } from './QuickButtons';
import { VariantModal } from './VariantModal';
import { usePOS } from '../context/POSContext';
import type { ProductSearchResult } from '../types';

export function ProductPanel() {
  const [variantProduct, setVariantProduct] = useState<ProductSearchResult | null>(null);
  const { addToCart } = usePOS();

  const handleProductSelect = (product: ProductSearchResult) => {
    if (product.variants && product.variants.length > 0) {
      setVariantProduct(product);
    } else {
      addToCart({
        productId: product.id,
        productName: product.name,
        sku: product.sku,
        unitPrice: product.price,
        originalPrice: product.price,
        quantity: 1,
        taxRate: 0,
        isTaxable: true,
        imageUrl: product.imageUrl,
      });
    }
  };

  return (
    <div className="flex h-full flex-col">
      {/* Panel Header */}
      <div className="flex shrink-0 items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <h2 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Products</h2>
      </div>

      {/* Search */}
      <div className="shrink-0 border-b border-gray-100 p-3 dark:border-gray-800">
        <ProductSearch onSelect={handleProductSelect} />
      </div>

      {/* Quick Buttons */}
      <div className="flex-1 overflow-y-auto p-4">
        <QuickButtons />
      </div>

      {/* Variant Modal */}
      <VariantModal
        product={variantProduct}
        open={!!variantProduct}
        onClose={() => setVariantProduct(null)}
      />
    </div>
  );
}
