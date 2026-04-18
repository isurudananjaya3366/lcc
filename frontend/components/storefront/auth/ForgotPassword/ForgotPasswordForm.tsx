'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2, Mail, Send } from 'lucide-react';
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  forgotPasswordSchema,
  type ForgotPasswordFormValues,
} from '@/lib/validations/forgotPasswordSchema';
import { requestPasswordReset } from '@/services/storefront/authService';
import { EmailSentMessage } from './EmailSentMessage';
import { OTPInput } from './OTPInput';

type Step = 'form' | 'emailSent' | 'otpVerify';

export function ForgotPasswordForm() {
  const [isPending, setIsPending] = useState(false);
  const [step, setStep] = useState<Step>('form');
  const [error, setError] = useState<string | null>(null);
  const [identifier, setIdentifier] = useState('');

  const form = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { identifier: '' },
  });

  function isEmail(value: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  }

  async function onSubmit(values: ForgotPasswordFormValues) {
    setIsPending(true);
    setError(null);

    try {
      await requestPasswordReset(values.identifier);
      setIdentifier(values.identifier);

      if (isEmail(values.identifier)) {
        setStep('emailSent');
      } else {
        setStep('otpVerify');
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to send reset request. Please try again.',
      );
    } finally {
      setIsPending(false);
    }
  }

  async function handleResend() {
    setIsPending(true);
    setError(null);
    try {
      await requestPasswordReset(identifier);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to resend. Please try again.',
      );
    } finally {
      setIsPending(false);
    }
  }

  if (step === 'emailSent') {
    return <EmailSentMessage email={identifier} onResend={handleResend} />;
  }

  if (step === 'otpVerify') {
    return <OTPInput identifier={identifier} onResend={handleResend} />;
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <FormField
          control={form.control}
          name="identifier"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email or Phone</FormLabel>
              <FormControl>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="you@example.com or +94XXXXXXXXX"
                    className="pl-10"
                    {...field}
                  />
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" className="w-full" disabled={isPending}>
          {isPending ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Send className="mr-2 h-4 w-4" />
          )}
          Send Reset Link
        </Button>
      </form>
    </Form>
  );
}
