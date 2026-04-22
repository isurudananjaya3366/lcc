import type { Metadata } from 'next';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

import { CreateProductForm } from './CreateProductForm';

export const metadata: Metadata = {
  title: 'Create Product',
  description: 'Add new product to your inventory catalog',
  robots: { index: false, follow: false },
};

export default function CreateProductPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {/* Page Header */}
      <div className="flex items-center gap-4">
        <Link
          href="/products"
          className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Products
        </Link>
      </div>

      <div>
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Create New Product</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Add a new product to your catalog
        </p>
      </div>

      <CreateProductForm />
    </div>
  );
}
