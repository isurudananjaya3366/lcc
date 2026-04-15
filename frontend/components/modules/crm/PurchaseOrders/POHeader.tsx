'use client';

import Link from 'next/link';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function POHeader() {
  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Purchase Orders</h1>
        <p className="text-sm text-muted-foreground">
          Manage purchase orders and track vendor deliveries
        </p>
      </div>
      <Button asChild>
        <Link href="/purchase-orders/new">
          <Plus className="mr-2 h-4 w-4" />
          Create PO
        </Link>
      </Button>
    </div>
  );
}
