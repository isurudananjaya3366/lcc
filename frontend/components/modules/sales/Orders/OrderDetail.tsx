'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useOrder } from '@/hooks/queries/useOrder';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { salesService } from '@/services/api/salesService';
import { salesKeys } from '@/lib/queryKeys';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import {
  OrderDetailsHeader,
  OrderStatusBanner,
  OrderInfoCard,
  OrderItemsTable,
  OrderTotals,
  OrderTimeline,
  OrderNotes,
  StatusUpdateModal,
  CancelOrderDialog,
} from './OrderDetails';
import type { OrderStatus } from '@/types/sales';

interface OrderDetailProps {
  orderId: string;
}

export function OrderDetail({ orderId }: OrderDetailProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { data: order, isLoading, error } = useOrder(orderId);
  const [statusModalOpen, setStatusModalOpen] = useState(false);
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);

  const updateOrderMutation = useMutation({
    mutationFn: (data: { orderStatus: OrderStatus; notes?: string }) =>
      salesService.updateOrder(orderId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salesKeys.order(orderId) });
      queryClient.invalidateQueries({ queryKey: salesKeys.orders() });
    },
  });

  const cancelOrderMutation = useMutation({
    mutationFn: (reason: string) => salesService.cancelOrder(orderId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salesKeys.order(orderId) });
      queryClient.invalidateQueries({ queryKey: salesKeys.orders() });
    },
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-16 w-full animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-4">
            <div className="h-40 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-64 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
          </div>
          <div className="space-y-4">
            <div className="h-64 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-48 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="flex min-h-[300px] flex-col items-center justify-center gap-3">
        <p className="text-lg font-medium text-gray-900 dark:text-gray-100">Order not found</p>
        <Link href="/orders">
          <Button variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Orders
          </Button>
        </Link>
      </div>
    );
  }

  const paymentStatusMap: Record<string, 'paid' | 'partial' | 'unpaid'> = {
    PAID: 'paid',
    PARTIAL: 'partial',
    UNPAID: 'unpaid',
    OVERPAID: 'paid',
    REFUNDED: 'unpaid',
  };

  return (
    <div className="space-y-6">
      {/* Back button + Header */}
      <div className="flex items-center gap-4">
        <Link href="/orders">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
      </div>

      <OrderDetailsHeader
        order={order}
        onEdit={() => router.push(`/orders/${orderId}?edit=true`)}
        onPrint={() => window.print()}
        onCancel={() => setCancelDialogOpen(true)}
      />

      <OrderStatusBanner
        status={order.orderStatus}
        onActionClick={() => setStatusModalOpen(true)}
      />

      {/* Two-column layout */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left Column */}
        <div className="space-y-6 lg:col-span-2">
          <OrderInfoCard order={order} />
          <OrderItemsTable items={order.items} />
          <OrderTotals
            subtotal={order.subtotal}
            discount={order.discountTotal}
            tax={order.taxTotal}
            shipping={order.shippingCost}
            total={order.total}
            paymentStatus={paymentStatusMap[order.paymentStatus]}
          />
        </div>

        {/* Right Column (sticky) */}
        <div className="space-y-6 lg:sticky lg:top-20 lg:self-start">
          <OrderTimeline timeline={[]} />
          <OrderNotes notes={order.notes || []} orderId={orderId} />
        </div>
      </div>

      {/* Modals */}
      <StatusUpdateModal
        isOpen={statusModalOpen}
        onClose={() => setStatusModalOpen(false)}
        order={order}
        onSubmit={async (data) => {
          await updateOrderMutation.mutateAsync({
            orderStatus: data.newStatus as OrderStatus,
            notes: data.notes,
          });
          setStatusModalOpen(false);
        }}
      />

      <CancelOrderDialog
        isOpen={cancelDialogOpen}
        onClose={() => setCancelDialogOpen(false)}
        order={order}
        onConfirm={async (reason) => {
          await cancelOrderMutation.mutateAsync(reason);
          setCancelDialogOpen(false);
        }}
      />
    </div>
  );
}
