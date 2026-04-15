'use client';

import Link from 'next/link';
import { ArrowLeft, Calendar, Building2, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Separator } from '@/components/ui/separator';
import { usePurchaseOrder } from '@/hooks/crm/usePurchaseOrders';
import { POStatusTimeline } from './POStatusTimeline';
import { POLineItemsTable } from './POLineItemsTable';
import { ReceiveItemsModal } from './ReceiveItemsModal';

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

const statusVariantMap: Record<string, StatusVariant> = {
  DRAFT: 'secondary',
  SENT: 'pending',
  ACKNOWLEDGED: 'confirmed',
  SHIPPED: 'shipped',
  RECEIVED: 'delivered',
  CANCELLED: 'cancelled',
};

interface PODetailsProps {
  poId: string;
}

export function PODetails({ poId }: PODetailsProps) {
  const { data, isLoading, error } = usePurchaseOrder(poId);
  const po = data?.data;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error || !po) {
    return (
      <div className="space-y-4">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/purchase-orders">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Purchase Orders
          </Link>
        </Button>
        <div className="flex flex-col items-center justify-center py-12">
          <p className="text-muted-foreground">Purchase order not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/purchase-orders">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight">PO #{po.poNumber}</h1>
              <Badge variant={statusVariantMap[po.status] ?? 'default'}>{po.status}</Badge>
            </div>
            <p className="text-sm text-muted-foreground">
              Created {new Date(po.createdAt).toLocaleDateString('en-LK')}
            </p>
          </div>
        </div>
        {['SHIPPED', 'ACKNOWLEDGED', 'SENT'].includes(po.status) && <ReceiveItemsModal po={po} />}
      </div>

      {/* Status Timeline */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Order Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <POStatusTimeline status={po.status} />
        </CardContent>
      </Card>

      {/* Order Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <Calendar className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground">Order Date</p>
              <p className="font-medium">{new Date(po.orderDate).toLocaleDateString('en-LK')}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <Calendar className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground">Expected Delivery</p>
              <p className="font-medium">
                {po.expectedDate ? new Date(po.expectedDate).toLocaleDateString('en-LK') : '—'}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 flex items-center gap-3">
            <Building2 className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground">Vendor</p>
              <Link
                href={`/vendors/${po.vendorId}`}
                className="font-medium text-primary hover:underline"
              >
                View Vendor
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Line Items */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Line Items ({po.items.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <POLineItemsTable po={po} />
        </CardContent>
      </Card>

      {/* Notes & Terms */}
      {(po.notes || po.terms) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {po.notes && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Notes</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">{po.notes}</p>
              </CardContent>
            </Card>
          )}
          {po.terms && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Terms & Conditions</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">{po.terms}</p>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Shipping Address */}
      {po.shippingAddress && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Shipping Address</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">
              {po.shippingAddress.street}
              {po.shippingAddress.street2 && `, ${po.shippingAddress.street2}`}
              <br />
              {po.shippingAddress.city}, {po.shippingAddress.state} {po.shippingAddress.postalCode}
              <br />
              {po.shippingAddress.country}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
