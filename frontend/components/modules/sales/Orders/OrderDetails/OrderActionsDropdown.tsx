'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MoreVertical, Edit, Printer, Copy, Mail, FileText, XCircle } from 'lucide-react';
import type { Order } from '@/types/sales';
import { OrderStatus } from '@/types/sales';

interface OrderActionsDropdownProps {
  order: Order;
  callbacks?: {
    onEdit?: () => void;
    onPrint?: () => void;
    onDuplicate?: () => void;
    onEmail?: () => void;
    onInvoice?: () => void;
    onCancel?: () => void;
  };
}

const editableStatuses: OrderStatus[] = [
  OrderStatus.DRAFT,
  OrderStatus.CONFIRMED,
  OrderStatus.PROCESSING,
  OrderStatus.PENDING,
];
const cancellableStatuses: OrderStatus[] = [
  OrderStatus.DRAFT,
  OrderStatus.CONFIRMED,
  OrderStatus.PROCESSING,
  OrderStatus.PENDING,
];
const invoiceableStatuses: OrderStatus[] = [
  OrderStatus.CONFIRMED,
  OrderStatus.PROCESSING,
  OrderStatus.SHIPPED,
  OrderStatus.DELIVERED,
  OrderStatus.COMPLETED,
];

export function OrderActionsDropdown({ order, callbacks }: OrderActionsDropdownProps) {
  const router = useRouter();
  const canEdit = editableStatuses.includes(order.orderStatus);
  const canCancel = cancellableStatuses.includes(order.orderStatus);
  const canInvoice = invoiceableStatuses.includes(order.orderStatus);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <MoreVertical className="h-4 w-4" />
          <span className="sr-only">More actions</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuItem
          disabled={!canEdit}
          onClick={() => callbacks?.onEdit?.() ?? router.push(`/orders/${order.id}?edit=true`)}
        >
          <Edit className="mr-2 h-4 w-4" />
          Edit Order
        </DropdownMenuItem>

        <DropdownMenuItem onClick={() => callbacks?.onPrint?.() ?? window.print()}>
          <Printer className="mr-2 h-4 w-4" />
          Print
        </DropdownMenuItem>

        <DropdownMenuItem onClick={callbacks?.onDuplicate}>
          <Copy className="mr-2 h-4 w-4" />
          Duplicate
        </DropdownMenuItem>

        <DropdownMenuItem onClick={callbacks?.onEmail}>
          <Mail className="mr-2 h-4 w-4" />
          Email to Customer
        </DropdownMenuItem>

        <DropdownMenuItem disabled={!canInvoice} onClick={callbacks?.onInvoice}>
          <FileText className="mr-2 h-4 w-4" />
          Generate Invoice
        </DropdownMenuItem>

        <DropdownMenuSeparator />

        <DropdownMenuItem
          disabled={!canCancel}
          onClick={callbacks?.onCancel}
          className="text-red-600 focus:text-red-600"
        >
          <XCircle className="mr-2 h-4 w-4" />
          Cancel Order
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
