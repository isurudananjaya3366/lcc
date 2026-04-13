import { toast } from 'sonner';

export interface ToastOptions {
  title?: string;
  description?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export interface PromiseMessages<T> {
  loading: string;
  success: string | ((data: T) => string);
  error: string | ((err: unknown) => string);
}

export function useToast() {
  return {
    success: (message: string, options?: ToastOptions) => {
      toast.success(options?.title ?? message, {
        description: options?.description,
        duration: options?.duration,
        action: options?.action
          ? { label: options.action.label, onClick: options.action.onClick }
          : undefined,
      });
    },
    error: (message: string, options?: ToastOptions) => {
      toast.error(options?.title ?? message, {
        description: options?.description,
        duration: options?.duration,
        action: options?.action
          ? { label: options.action.label, onClick: options.action.onClick }
          : undefined,
      });
    },
    warning: (message: string, options?: ToastOptions) => {
      toast.warning(options?.title ?? message, {
        description: options?.description,
        duration: options?.duration,
      });
    },
    info: (message: string, options?: ToastOptions) => {
      toast.info(options?.title ?? message, {
        description: options?.description,
        duration: options?.duration,
      });
    },
    loading: (message: string, options?: ToastOptions) => {
      return toast.loading(options?.title ?? message, {
        description: options?.description,
      });
    },
    promise: <T,>(promise: Promise<T>, messages: PromiseMessages<T>) => {
      return toast.promise(promise, {
        loading: messages.loading,
        success: messages.success,
        error: messages.error,
      });
    },
    dismiss: (toastId?: string | number) => {
      toast.dismiss(toastId);
    },
  };
}
