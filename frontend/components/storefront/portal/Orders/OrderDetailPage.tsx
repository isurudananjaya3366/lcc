'use client';

import { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { getOrderById } from '@/services/storefront/portalService';
import type { PortalOrder } from '@/types/storefront/portal.types';
import { OrderHeader } from './OrderHeader';
import { OrderTracking } from './OrderTracking';
import { OrderItemsSection } from './OrderItemsSection';
import { ShippingAddressCard } from './ShippingAddressCard';
import { PaymentInfoCard } from './PaymentInfoCard';
import { OrderSummaryCard } from './OrderSummaryCard';
import { ReorderButton } from './ReorderButton';
import { DownloadInvoice } from './DownloadInvoice';
import { ContactSupport } from './ContactSupport';
import { OrderDetailLoading } from './OrderDetailLoading';

interface OrderDetailPageProps {
  orderId: string;
}

export function OrderDetailPage({ orderId }: OrderDetailPageProps) {
  const [order, setOrder] = useState<PortalOrder | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchOrder() {
      try {
        setLoading(true);
        setError(null);
        const data = await getOrderById(orderId);
        if (!cancelled) {
          setOrder(data);
        }
      } catch {
        if (!cancelled) {
          setError('Failed to load order details. Please try again.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchOrder();
    return () => {
      cancelled = true;
    };
  }, [orderId]);

  if (loading) {
    return <OrderDetailLoading />;
  }

  if (error || !order) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-16 text-center">
        <AlertCircle className="h-12 w-12 text-destructive" />
        <p className="text-lg font-medium">{error ?? 'Order not found'}</p>
        <Button variant="outline" onClick={() => window.location.reload()}>
          Try Again
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <OrderHeader order={order} />
      <OrderTracking status={order.status} updatedAt={order.updatedAt} />
      <OrderItemsSection items={order.items} />

      <div className="grid gap-4 md:grid-cols-2">
        <ShippingAddressCard address={order.shippingAddress} />
        <PaymentInfoCard paymentMethod={order.paymentMethod} />
      </div>

      <OrderSummaryCard order={order} />

      <div className="flex flex-wrap gap-3">
        <ReorderButton items={order.items} />
        <DownloadInvoice orderId={order.id} />
        <ContactSupport orderNumber={order.orderNumber} />
      </div>
    </div>
  );
}
