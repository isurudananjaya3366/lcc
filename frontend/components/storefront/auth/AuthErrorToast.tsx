'use client';

import { toast } from 'sonner';

export function showAuthError(message: string) {
  toast.error(message, {
    duration: 5000,
  });
}

export function showAuthSuccess(message: string) {
  toast.success(message, {
    duration: 3000,
  });
}
