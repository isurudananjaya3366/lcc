'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import salesService from '@/services/api/salesService';
import { salesKeys } from '@/lib/queryKeys';
import type { OrderShipment } from '@/types/sales';

export function useCreateShipment(orderId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (shipment: Omit<OrderShipment, 'id'>) =>
      salesService.createShipment(orderId, shipment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salesKeys.order(orderId) });
      queryClient.invalidateQueries({ queryKey: salesKeys.orders() });
    },
  });
}

export function useMarkDelivered(orderId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (shipmentId: string) => salesService.markDelivered(orderId, shipmentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salesKeys.order(orderId) });
      queryClient.invalidateQueries({ queryKey: salesKeys.orders() });
    },
  });
}
