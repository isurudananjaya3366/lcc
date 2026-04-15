'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm, Controller, type Resolver } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { quoteFormSchema, type QuoteFormValues } from '@/lib/validations/quote';
import { useCreateQuote } from '@/hooks/queries/useQuotes';
import { CustomerSelect } from './CustomerSelect';
import { QuoteItemsSection } from './QuoteItemsSection';
import { QuoteValiditySection } from './QuoteValiditySection';

function formatCurrency(amount: number): string {
  return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

export function NewQuoteForm() {
  const router = useRouter();
  const createQuote = useCreateQuote();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
    formState: { errors },
  } = useForm<QuoteFormValues>({
    resolver: zodResolver(quoteFormSchema) as Resolver<QuoteFormValues>,
    defaultValues: {
      customerId: '',
      expiryDate: '',
      items: [{ productId: '', productName: '', quantity: 1, unitPrice: 0, discountPercent: 0 }],
      terms: '',
      notes: '',
    },
  });

  const watchItems = watch('items');
  const watchExpiry = watch('expiryDate');

  const subtotal = watchItems.reduce((sum, item) => {
    const lineTotal = (item.quantity || 0) * (item.unitPrice || 0);
    const discount = (item.discountPercent || 0) / 100;
    return sum + lineTotal * (1 - discount);
  }, 0);

  const onSubmit = async (data: QuoteFormValues) => {
    setSubmitError(null);
    try {
      await createQuote.mutateAsync({
        customerId: data.customerId,
        expiryDate: data.expiryDate,
        items: data.items.map((item) => ({
          productId: item.productId,
          productName: item.productName,
          quantity: item.quantity,
          unitPrice: item.unitPrice,
        })),
        terms: data.terms,
        notes: data.notes,
      });
      router.push('/quotes');
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Failed to create quote');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/quotes">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Create New Quote</h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Customer Selection - Task 73 */}
        <Card>
          <CardContent className="pt-6">
            <Controller
              name="customerId"
              control={control}
              render={({ field }) => (
                <CustomerSelect
                  value={field.value}
                  onChange={field.onChange}
                  error={errors.customerId?.message}
                />
              )}
            />
          </CardContent>
        </Card>

        {/* Line Items - Task 74 */}
        <QuoteItemsSection control={control} register={register} watch={watch} errors={errors} />

        {/* Validity & Terms - Task 75 */}
        <QuoteValiditySection
          register={register}
          errors={errors}
          expiryDate={watchExpiry}
          onExpiryChange={(value) => setValue('expiryDate', value)}
        />

        {/* Summary & Submit */}
        <Card>
          <CardContent className="flex items-center justify-between pt-6">
            <div className="text-lg font-bold">Subtotal: {formatCurrency(subtotal)}</div>
            <div className="flex gap-3">
              <Link href="/quotes">
                <Button type="button" variant="outline">
                  Cancel
                </Button>
              </Link>
              {submitError && <p className="self-center text-sm text-red-500">{submitError}</p>}
              <Button type="submit" disabled={createQuote.isPending}>
                {createQuote.isPending ? 'Creating...' : 'Create Quote'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  );
}
