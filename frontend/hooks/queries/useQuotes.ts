/**
 * useQuotes — fetch paginated quote list
 * useQuoteDetails — fetch single quote
 * useCreateQuote, useSendQuote, useDeleteQuote — mutations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { salesKeys } from '@/lib/queryKeys';
import { quoteService } from '@/services/api/quoteService';
import type { QuoteSearchParams, QuoteCreateRequest } from '@/types/quotes';

export function useQuotes(filters?: QuoteSearchParams) {
  return useQuery({
    queryKey: [...salesKeys.quotes(), filters],
    queryFn: () => quoteService.getQuotes(filters),
    staleTime: 1 * 60 * 1000,
    placeholderData: (prev) => prev,
    refetchOnWindowFocus: true,
  });
}

export function useQuoteDetails(quoteId: string) {
  return useQuery({
    queryKey: salesKeys.quote(quoteId),
    queryFn: () => quoteService.getQuoteById(quoteId),
    select: (res) => res.data,
    enabled: !!quoteId,
  });
}

export function useCreateQuote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: QuoteCreateRequest) => quoteService.createQuote(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salesKeys.quotes() });
    },
  });
}

export function useSendQuote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, email }: { id: string; email?: string }) =>
      quoteService.sendQuote(id, email),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salesKeys.quotes() });
    },
  });
}

export function useDeleteQuote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => quoteService.deleteQuote(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salesKeys.quotes() });
    },
  });
}
