'use client';

import { useState } from 'react';
import { Search, Package } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useVendorProducts } from '@/hooks/crm/useVendors';

interface ProductsTabProps {
  vendorId: string;
}

export function ProductsTab({ vendorId }: ProductsTabProps) {
  const [search, setSearch] = useState('');
  const { data, isLoading } = useVendorProducts(vendorId);

  const products = data?.data ?? [];
  const filtered = search
    ? products.filter(
        (p) =>
          p.vendorSKU?.toLowerCase().includes(search.toLowerCase()) ||
          p.productId.toLowerCase().includes(search.toLowerCase())
      )
    : products;

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-64" />
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <Package className="h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium">No Products</h3>
        <p className="text-sm text-muted-foreground">No products are linked to this vendor yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">
          Products
          <Badge variant="secondary" className="ml-2">
            {products.length}
          </Badge>
        </h3>
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search products..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Product ID</TableHead>
            <TableHead>Vendor SKU</TableHead>
            <TableHead className="text-right">Unit Cost</TableHead>
            <TableHead className="text-center">MOQ</TableHead>
            <TableHead className="text-center">Lead Time</TableHead>
            <TableHead>Last Purchase</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filtered.map((product) => (
            <TableRow key={product.id}>
              <TableCell className="font-medium">{product.productId}</TableCell>
              <TableCell>{product.vendorSKU || '—'}</TableCell>
              <TableCell className="text-right">
                ₨{product.unitCost.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
              </TableCell>
              <TableCell className="text-center">{product.moq}</TableCell>
              <TableCell className="text-center">{product.leadTimeDays}d</TableCell>
              <TableCell className="text-sm text-muted-foreground">
                {product.lastPurchaseDate
                  ? new Date(product.lastPurchaseDate).toLocaleDateString('en-LK', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })
                  : '—'}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
