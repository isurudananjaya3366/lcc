'use client';

import Link from 'next/link';
import { MoreHorizontal, Eye, Edit, ArrowRightLeft, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface StockActionsCellProps {
  productId: string;
  warehouseId: string;
}

export function StockActionsCell({ productId, warehouseId }: StockActionsCellProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
          <span className="sr-only">Open menu</span>
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem asChild>
          <Link href={`/products/${productId}`}>
            <Eye className="mr-2 h-4 w-4" />
            View Details
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <Link href={`/inventory/adjustments/new?product=${productId}&warehouse=${warehouseId}`}>
            <Edit className="mr-2 h-4 w-4" />
            Quick Adjust
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <Link href={`/inventory/transfers/new?product=${productId}&from=${warehouseId}`}>
            <ArrowRightLeft className="mr-2 h-4 w-4" />
            Transfer
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <Link href={`/inventory/movements?product=${productId}`}>
            <Clock className="mr-2 h-4 w-4" />
            View History
          </Link>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
