'use client';

import { Suspense } from 'react';
import { WarehouseForm } from '@/components/modules/inventory/Warehouses';

interface EditWarehouseClientProps {
  warehouseId: string;
}

export function EditWarehouseClient({ warehouseId }: EditWarehouseClientProps) {
  return (
    <Suspense fallback={<EditWarehouseSkeleton />}>
      <WarehouseForm warehouseId={warehouseId} />
    </Suspense>
  );
}

function EditWarehouseSkeleton() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="flex items-center justify-between">
        <div className="h-8 w-48 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="flex gap-2">
          <div className="h-10 w-24 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-10 w-24 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
      </div>
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="space-y-3 rounded-lg border p-6">
          <div className="h-6 w-32 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="grid grid-cols-2 gap-4">
            <div className="h-10 rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-10 rounded bg-gray-200 dark:bg-gray-700" />
          </div>
        </div>
      ))}
    </div>
  );
}
