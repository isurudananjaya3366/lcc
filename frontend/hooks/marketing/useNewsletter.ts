'use client';

import { useMutation } from '@tanstack/react-query';
import * as newsletterApi from '@/lib/marketing/newsletter';
import type { SubscribeRequest, SubscribeResponse } from '@/types/marketing/newsletter.types';

export function useNewsletterSubscribe() {
  return useMutation<SubscribeResponse, Error, SubscribeRequest>({
    mutationFn: (data) => newsletterApi.subscribe(data),
  });
}

export function useNewsletterUnsubscribe() {
  return useMutation({
    mutationFn: ({ email, token }: { email: string; token: string }) =>
      newsletterApi.unsubscribe(email, token),
  });
}

export function useNewsletterConfirm() {
  return useMutation({
    mutationFn: (token: string) => newsletterApi.confirmSubscription(token),
  });
}
