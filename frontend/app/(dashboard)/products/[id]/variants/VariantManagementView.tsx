'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Plus } from 'lucide-react';
import type { Product, ProductVariant, ProductStatus } from '@/types/product';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { VariantManager } from '@/components/modules/products/Variants';

// TODO: Replace with actual API data via TanStack Query
const MOCK_PRODUCT: Product = {
  id: 'demo-1',
  tenantId: 'tenant-1',
  sku: 'PROD-001',
  name: 'Sample Product',
  productType: 'VARIABLE' as const,
  status: 'ACTIVE' as unknown as ProductStatus,
  unitOfMeasure: 'PIECE' as const,
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
  isActive: true,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

interface VariantManagementViewProps {
  productId: string;
}

export function VariantManagementView({ productId }: VariantManagementViewProps) {
  const [showCreate, setShowCreate] = useState(false);
  const product = { ...MOCK_PRODUCT, id: productId };
  const variants: ProductVariant[] = [];

  const activeCount = variants.filter((v) => v.isActive).length;
  const totalStock = variants.reduce((sum, v) => sum + v.stockQuantity, 0);

  return (
    <div className="space-y-6">
      <Link
        href={`/products/${productId}`}
        className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Product
      </Link>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
            Manage Variants
          </h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {product.name} &middot; {product.sku}
          </p>
        </div>
        {!showCreate && (
          <Button onClick={() => setShowCreate(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Generate Variants
          </Button>
        )}
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="pt-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">Total Variants</p>
            <p className="mt-1 text-2xl font-bold tabular-nums">{variants.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">Active</p>
            <p className="mt-1 text-2xl font-bold tabular-nums text-green-600 dark:text-green-400">
              {activeCount}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">Total Stock</p>
            <p className="mt-1 text-2xl font-bold tabular-nums">{totalStock}</p>
          </CardContent>
        </Card>
      </div>

      {/* Variant Manager */}
      <VariantManager product={product} variants={variants} />
    </div>
  );
}
