'use client';

import { Badge } from '@/components/ui/badge';
import type { PurchaseOrder } from '@/types/vendor';
import { POActionsCell } from './POActionsCell';

type StatusVariant =
  | 'default'
  | 'secondary'
  | 'destructive'
  | 'outline'
  | 'pending'
  | 'confirmed'
  | 'processing'
  | 'shipped'
  | 'delivered'
  | 'cancelled'
  | 'failed';

const statusConfig: Record<PurchaseOrder['status'], { label: string; variant: StatusVariant }> = {
  DRAFT: { label: 'Draft', variant: 'secondary' },
  SENT: { label: 'Sent', variant: 'pending' },
  ACKNOWLEDGED: { label: 'Acknowledged', variant: 'confirmed' },
  SHIPPED: { label: 'Shipped', variant: 'shipped' },
  RECEIVED: { label: 'Received', variant: 'delivered' },
  CANCELLED: { label: 'Cancelled', variant: 'cancelled' },
};

export interface POTableColumn {
  key: string;
  label: string;
  sortable?: boolean;
  render: (po: PurchaseOrder) => React.ReactNode;
}

export const poTableColumns: POTableColumn[] = [
  {
    key: 'poNumber',
    label: 'PO Number',
    sortable: true,
    render: (po) => <span className="font-medium">{po.poNumber}</span>,
  },
  {
    key: 'orderDate',
    label: 'Order Date',
    sortable: true,
    render: (po) => new Date(po.orderDate).toLocaleDateString('en-LK'),
  },
  {
    key: 'expectedDate',
    label: 'Expected Date',
    render: (po) => (po.expectedDate ? new Date(po.expectedDate).toLocaleDateString('en-LK') : '—'),
  },
  {
    key: 'items',
    label: 'Items',
    render: (po) => <span>{po.items.length} items</span>,
  },
  {
    key: 'total',
    label: 'Total',
    sortable: true,
    render: (po) => (
      <span className="font-medium">
        ₨ {po.total.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
      </span>
    ),
  },
  {
    key: 'status',
    label: 'Status',
    render: (po) => {
      const config = statusConfig[po.status];
      return <Badge variant={config.variant}>{config.label}</Badge>;
    },
  },
  {
    key: 'actions',
    label: '',
    render: (po) => <POActionsCell po={po} />,
  },
];
