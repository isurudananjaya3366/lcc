'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { salesService } from '@/services/api/salesService';
import { salesKeys } from '@/lib/queryKeys';
import type { OrderPayment } from '@/types/sales';

export function useRecordPayment(orderId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payment: Omit<OrderPayment, 'id' | 'createdAt'>) =>
      salesService.recordPayment(orderId, payment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salesKeys.order(orderId) });
      queryClient.invalidateQueries({ queryKey: salesKeys.orders() });
    },
  });
}

export function useRefundPayment(orderId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      paymentId,
      amount,
      reason,
    }: {
      paymentId: string;
      amount: number;
      reason: string;
    }) => salesService.refundPayment(orderId, paymentId, amount, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salesKeys.order(orderId) });
      queryClient.invalidateQueries({ queryKey: salesKeys.orders() });
    },
  });
}
