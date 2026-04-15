'use client';

import { useState, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import type { Product, ProductStatus } from '@/types/product';
import { ProductType, UnitOfMeasure } from '@/types/product';
import {
  ProductDetailHeader,
  ProductInfoCard,
  ProductPricingCard,
  ProductInventoryCard,
  ProductImageGallery,
  ProductActivityTimeline,
  DeleteProductDialog,
} from '@/components/modules/products/ProductDetail';
import type { ActivityItem } from '@/components/modules/products/ProductDetail';

// TODO: Replace with actual API calls
const MOCK_PRODUCT: Product = {
  id: 'demo-1',
  tenantId: 'tenant-1',
  sku: 'PROD-001',
  name: 'Sample Product',
  description: 'This is a sample product for development purposes.',
  productType: ProductType.SIMPLE,
  status: 'ACTIVE' as unknown as ProductStatus,
  categoryId: 'cat-1',
  unitOfMeasure: UnitOfMeasure.PIECE,
  pricing: {
    basePrice: 2500,
    cost: 1800,
    margin: 38.9,
    taxRate: 12,
    taxInclusive: false,
    currencyCode: 'LKR',
  },
  inventory: {
    trackInventory: true,
    stockQuantity: 150,
    lowStockThreshold: 20,
    allowBackorder: false,
    requiresSerial: false,
  },
  images: [],
  tags: ['electronics', 'featured'],
  isActive: true,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

const MOCK_ACTIVITIES: ActivityItem[] = [
  {
    id: '1',
    type: 'created',
    description: 'Product created',
    user: 'Admin',
    timestamp: new Date().toISOString(),
  },
];

interface ProductDetailViewProps {
  productId: string;
}

export function ProductDetailView({ productId }: ProductDetailViewProps) {
  const router = useRouter();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  // TODO: Replace with useProduct hook / TanStack Query
  const product = { ...MOCK_PRODUCT, id: productId };
  const activities = MOCK_ACTIVITIES;

  const handleDelete = useCallback(async () => {
    // TODO: Call delete API
    console.log('Deleting product:', productId);
    setDeleteDialogOpen(false);
    router.push('/products');
  }, [productId, router]);

  const handleArchive = useCallback(async () => {
    // TODO: Call archive/restore API
    console.log('Archive/restore product:', productId);
  }, [productId]);

  const handleDuplicate = useCallback(() => {
    // TODO: Duplicate product - pre-fill form, append "(Copy)", clear ID/SKU
    console.log('Duplicate product:', productId);
    router.push('/products/new');
  }, [productId, router]);

  return (
    <div className="space-y-6">
      {/* Back link */}
      <Link
        href="/products"
        className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Products
      </Link>

      {/* Header */}
      <ProductDetailHeader
        product={product}
        onDelete={() => setDeleteDialogOpen(true)}
        onArchive={handleArchive}
        onDuplicate={handleDuplicate}
      />

      {/* Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left column */}
        <div className="space-y-6 lg:col-span-2">
          <ProductInfoCard product={product} />
          <ProductPricingCard product={product} />
          <ProductInventoryCard product={product} />
        </div>

        {/* Right column */}
        <div className="space-y-6">
          <ProductImageGallery images={product.images || []} />
          <ProductActivityTimeline activities={activities} />
        </div>
      </div>

      {/* Delete Dialog */}
      <DeleteProductDialog
        product={product}
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        onConfirm={handleDelete}
      />
    </div>
  );
}
