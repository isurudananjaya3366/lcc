/**
 * useQuoteConversion — Convert a quote to an order
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { salesKeys } from '@/lib/queryKeys';
import { quoteService } from '@/services/api/quoteService';
import type { QuoteConversionRequest } from '@/types/quotes';

export function useQuoteConversion() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: (payload: QuoteConversionRequest) => quoteService.convertToOrder(payload),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: salesKeys.quotes() });
      queryClient.invalidateQueries({ queryKey: salesKeys.orders() });
      if (result.data?.orderId) {
        router.push(`/orders/${result.data.orderId}`);
      }
    },
  });
}
