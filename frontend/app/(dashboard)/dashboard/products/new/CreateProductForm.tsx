'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ProductForm } from '@/components/modules/products/ProductForm';
import type { ProductFormData } from '@/lib/validations/product';

export function CreateProductForm() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (data: ProductFormData) => {
    setIsLoading(true);
    try {
      // TODO: Wire to API — useCreateProduct mutation
      console.log('Creating product:', data);
      router.push('/products');
    } catch (error) {
      console.error('Failed to create product:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return <ProductForm onSubmit={handleSubmit} isLoading={isLoading} />;
}
