'use client';

import { formatDistanceToNow, format } from 'date-fns';
import type { Product } from '@/types/product';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface ProductInfoCardProps {
  product: Product;
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  const daysDiff = (Date.now() - date.getTime()) / (1000 * 60 * 60 * 24);
  if (daysDiff < 7) {
    return formatDistanceToNow(date, { addSuffix: true });
  }
  return format(date, 'MMM d, yyyy');
}

export function ProductInfoCard({ product }: ProductInfoCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Product Information</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* SKU */}
        <div>
          <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">SKU</dt>
          <dd className="mt-1">
            <Badge variant="outline" className="font-mono text-xs">
              {product.sku}
            </Badge>
          </dd>
        </div>

        {/* Description */}
        {product.description && (
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Description</dt>
            <dd className="mt-1 text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line">
              {product.description}
            </dd>
          </div>
        )}

        {/* Category */}
        {product.categoryId && (
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Category</dt>
            <dd className="mt-1">
              <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
                {product.categoryId}
              </Badge>
            </dd>
          </div>
        )}

        {/* Tags */}
        {product.tags && product.tags.length > 0 && (
          <div>
            <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Tags</dt>
            <dd className="mt-1 flex flex-wrap gap-1">
              {product.tags.map((tag) => (
                <Badge key={tag} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </dd>
          </div>
        )}

        {/* Dates */}
        <div className="grid grid-cols-2 gap-4 border-t pt-4 dark:border-gray-700">
          <div>
            <dt className="text-xs font-medium text-gray-500 dark:text-gray-400">Created</dt>
            <dd className="mt-0.5 text-sm text-gray-700 dark:text-gray-300">
              {formatDate(product.createdAt)}
            </dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-gray-500 dark:text-gray-400">Updated</dt>
            <dd className="mt-0.5 text-sm text-gray-700 dark:text-gray-300">
              {formatDate(product.updatedAt)}
            </dd>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
