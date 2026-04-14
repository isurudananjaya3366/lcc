'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { ProductForm } from '@/components/modules/products/ProductForm';
import type { ProductFormData } from '@/lib/validations/product';

interface EditProductFormProps {
  productId: string;
}

// TODO: Replace with actual API data fetching via TanStack Query useProduct hook
const MOCK_INITIAL_DATA: ProductFormData = {
  name: 'Sample Product',
  sku: 'PROD-001',
  description: 'This is a sample product for development purposes.',
  cost_price: 1800,
  selling_price: 2500,
  tax_category_id: 'standard',
  track_inventory: true,
  initial_stock: 150,
  reorder_point: 20,
  category_ids: [],
  tags: ['electronics', 'featured'],
  images: [],
};

export function EditProductForm({ productId }: EditProductFormProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (data: ProductFormData) => {
    setIsLoading(true);
    try {
      // TODO: Call update API - productService.updateProduct(productId, data)
      console.log('Updating product:', productId, data);
      router.push(`/products/${productId}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Link
        href={`/products/${productId}`}
        className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Product
      </Link>

      <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Edit Product</h2>

      <ProductForm initialData={MOCK_INITIAL_DATA} onSubmit={handleSubmit} isLoading={isLoading} />
    </div>
  );
}
