'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { CategoryForm } from '@/components/modules/products/Categories';
import type { ProductCategory } from '@/types/product';

// TODO: Replace with API data
const MOCK_CATEGORIES: ProductCategory[] = [
  {
    id: '1',
    name: 'Electronics',
    slug: 'electronics',
    displayOrder: 1,
    isActive: true,
    productCount: 45,
  },
  {
    id: '4',
    name: 'Clothing',
    slug: 'clothing',
    displayOrder: 2,
    isActive: true,
    productCount: 80,
  },
  {
    id: '7',
    name: 'Accessories',
    slug: 'accessories',
    displayOrder: 3,
    isActive: false,
    productCount: 0,
  },
];

export function CreateCategoryForm() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (data: Record<string, unknown>, imageFile: File | null) => {
    setIsSubmitting(true);
    try {
      // TODO: Call API to create category
      console.log('Creating category:', data, imageFile);
      router.push('/products/categories');
    } catch (error) {
      console.error('Failed to create category:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <CategoryForm
      mode="create"
      categories={MOCK_CATEGORIES}
      existingSlugs={MOCK_CATEGORIES.map((c) => c.slug)}
      onSubmit={handleSubmit}
      onCancel={() => router.push('/products/categories')}
      isSubmitting={isSubmitting}
    />
  );
}
