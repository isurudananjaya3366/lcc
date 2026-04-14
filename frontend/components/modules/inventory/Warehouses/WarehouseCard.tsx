'use client';

import { useState } from 'react';
import Link from 'next/link';
import { MapPin, MoreVertical, Pencil, Trash2 } from 'lucide-react';

import type { Warehouse } from '@/types/inventory';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';

import { WarehouseStats } from './WarehouseStats';
import { DeleteWarehouseDialog } from './DeleteWarehouseDialog';

interface WarehouseCardProps {
  warehouse: Warehouse;
}

export function WarehouseCard({ warehouse }: WarehouseCardProps) {
  const [showDelete, setShowDelete] = useState(false);

  const address = [warehouse.address.street, warehouse.address.city, warehouse.address.state]
    .filter(Boolean)
    .join(', ');

  return (
    <>
      <div
        className={cn(
          'flex flex-col rounded-lg border bg-white shadow-sm transition-shadow hover:shadow-md dark:bg-gray-900',
          warehouse.isActive
            ? 'border-gray-200 dark:border-gray-700'
            : 'border-gray-200/50 opacity-70 dark:border-gray-700/50'
        )}
      >
        {/* Header */}
        <div className="flex items-start justify-between border-b border-gray-100 p-4 dark:border-gray-800">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">{warehouse.name}</h3>
              <span className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                {warehouse.code}
              </span>
            </div>
            {warehouse.isPrimary && (
              <span className="mt-1 inline-block rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
                Primary
              </span>
            )}
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem asChild>
                <Link href={`/inventory/warehouses/${warehouse.id}`}>
                  <Pencil className="mr-2 h-3.5 w-3.5" />
                  Edit
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem
                className="text-red-600 dark:text-red-400"
                onClick={() => setShowDelete(true)}
              >
                <Trash2 className="mr-2 h-3.5 w-3.5" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Body - Address */}
        <div className="flex-1 p-4">
          <div className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400">
            <MapPin className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{address || 'No address provided'}</span>
          </div>
        </div>

        {/* Footer - Stats */}
        <div className="border-t border-gray-100 p-4 dark:border-gray-800">
          <WarehouseStats warehouse={warehouse} />
        </div>
      </div>

      <DeleteWarehouseDialog
        warehouse={warehouse}
        open={showDelete}
        onClose={() => setShowDelete(false)}
      />
    </>
  );
}
