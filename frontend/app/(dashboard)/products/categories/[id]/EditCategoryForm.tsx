'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { CategoryForm, DeleteCategoryDialog } from '@/components/modules/products/Categories';
import { Button } from '@/components/ui/button';
import { Trash2 } from 'lucide-react';
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

interface EditCategoryFormProps {
  categoryId: string;
}

export function EditCategoryForm({ categoryId }: EditCategoryFormProps) {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showDelete, setShowDelete] = useState(false);

  // TODO: Replace with API fetch
  const category: ProductCategory = MOCK_CATEGORIES.find((c) => c.id === categoryId) || {
    id: categoryId,
    name: 'Sample Category',
    slug: 'sample-category',
    description: 'A sample category for editing',
    displayOrder: 0,
    isActive: true,
    productCount: 0,
  };

  const handleSubmit = async (data: Record<string, unknown>, imageFile: File | null) => {
    setIsSubmitting(true);
    try {
      // TODO: Call API to update category
      console.log('Updating category:', categoryId, data, imageFile);
      router.push('/products/categories');
    } catch (error) {
      console.error('Failed to update category:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteConfirm = () => {
    // TODO: Call API to delete category
    setShowDelete(false);
    router.push('/products/categories');
  };

  return (
    <>
      <CategoryForm
        mode="edit"
        initialData={category}
        categories={MOCK_CATEGORIES}
        existingSlugs={MOCK_CATEGORIES.map((c) => c.slug)}
        onSubmit={handleSubmit}
        onCancel={() => router.push('/products/categories')}
        isSubmitting={isSubmitting}
      />

      <div className="mt-6 border-t pt-6">
        <Button variant="destructive" onClick={() => setShowDelete(true)}>
          <Trash2 className="mr-2 h-4 w-4" />
          Delete Category
        </Button>
      </div>

      <DeleteCategoryDialog
        category={category}
        isOpen={showDelete}
        onClose={() => setShowDelete(false)}
        onConfirm={handleDeleteConfirm}
        categories={MOCK_CATEGORIES}
      />
    </>
  );
}
