'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { Loader2, Smartphone, RefreshCw } from 'lucide-react';
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { otpSchema, type OTPFormValues } from '@/lib/validations/otpSchema';
import { verifyOTP } from '@/services/storefront/authService';

interface OTPInputProps {
  identifier: string;
  onResend: () => Promise<void>;
}

export function OTPInput({ identifier, onResend }: OTPInputProps) {
  const router = useRouter();
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cooldown, setCooldown] = useState(60);
  const [isResending, setIsResending] = useState(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const [digits, setDigits] = useState<string[]>(Array(6).fill(''));

  const form = useForm<OTPFormValues>({
    resolver: zodResolver(otpSchema),
    defaultValues: { otp: '' },
  });

  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = setInterval(() => {
      setCooldown((prev) => prev - 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [cooldown]);

  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  function handleDigitChange(index: number, value: string) {
    if (value && !/^\d$/.test(value)) return;

    const newDigits = [...digits];
    newDigits[index] = value;
    setDigits(newDigits);

    const otp = newDigits.join('');
    form.setValue('otp', otp, { shouldValidate: otp.length === 6 });

    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  }

  function handleKeyDown(index: number, e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Backspace' && !digits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  }

  function handlePaste(e: React.ClipboardEvent) {
    e.preventDefault();
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    if (!pasted) return;

    const newDigits = Array(6).fill('');
    for (let i = 0; i < pasted.length; i++) {
      newDigits[i] = pasted[i];
    }
    setDigits(newDigits);
    form.setValue('otp', newDigits.join(''), { shouldValidate: true });

    const focusIndex = Math.min(pasted.length, 5);
    inputRefs.current[focusIndex]?.focus();
  }

  const handleResend = useCallback(async () => {
    setIsResending(true);
    try {
      await onResend();
      setCooldown(60);
      setDigits(Array(6).fill(''));
      form.setValue('otp', '');
      inputRefs.current[0]?.focus();
    } finally {
      setIsResending(false);
    }
  }, [onResend, form]);

  async function onSubmit(values: OTPFormValues) {
    setIsPending(true);
    setError(null);

    try {
      const isEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(identifier);
      const result = await verifyOTP({
        otp: values.otp,
        email: isEmail ? identifier : '',
        phone: isEmail ? undefined : identifier,
      });

      if (result.verified) {
        router.push(
          `/account/reset-password?token=${encodeURIComponent(values.otp)}&email=${encodeURIComponent(identifier)}`,
        );
      } else {
        setError('Invalid OTP. Please try again.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Verification failed. Please try again.');
    } finally {
      setIsPending(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-center gap-2 text-center">
        <Smartphone className="h-5 w-5 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">
          We&apos;ve sent a 6-digit code to{' '}
          <span className="font-medium text-foreground">{identifier}</span>
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <FormField
            control={form.control}
            name="otp"
            render={() => (
              <FormItem>
                <FormLabel className="sr-only">OTP Code</FormLabel>
                <FormControl>
                  <div className="flex justify-center gap-2" onPaste={handlePaste}>
                    {digits.map((digit, index) => (
                      <Input
                        key={index}
                        ref={(el) => {
                          inputRefs.current[index] = el;
                        }}
                        type="text"
                        inputMode="numeric"
                        maxLength={1}
                        value={digit}
                        onChange={(e) => handleDigitChange(index, e.target.value)}
                        onKeyDown={(e) => handleKeyDown(index, e)}
                        className="h-12 w-12 text-center text-lg font-semibold"
                        aria-label={`Digit ${index + 1}`}
                      />
                    ))}
                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <Button type="submit" className="w-full" disabled={isPending}>
            {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Verify OTP
          </Button>
        </form>
      </Form>

      <div className="flex items-center justify-center gap-2">
        <span className="text-sm text-muted-foreground">Didn&apos;t receive the code?</span>
        <Button
          variant="link"
          size="sm"
          className="h-auto p-0"
          disabled={cooldown > 0 || isResending}
          onClick={handleResend}
        >
          {isResending && <RefreshCw className="mr-1 h-3 w-3 animate-spin" />}
          {cooldown > 0 ? `Resend in ${cooldown}s` : 'Resend'}
        </Button>
      </div>
    </div>
  );
}
