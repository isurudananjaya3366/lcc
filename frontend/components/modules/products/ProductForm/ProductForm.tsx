'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';

import {
  productFormSchema,
  type ProductFormData,
  productFormDefaults,
} from '@/lib/validations/product';
import { Form } from '@/components/ui/form';
import { Button } from '@/components/ui/button';

import { BasicInfoSection } from './BasicInfoSection';
import { PricingSection } from './PricingSection';
import { InventorySection } from './InventorySection';
import { CategorizationSection } from './CategorizationSection';
import { MediaSection } from './MediaSection';

interface ProductFormProps {
  initialData?: Partial<ProductFormData>;
  onSubmit: (data: ProductFormData) => void | Promise<void>;
  isLoading?: boolean;
}

export function ProductForm({
  initialData,
  onSubmit,
  isLoading = false,
}: ProductFormProps) {
  const router = useRouter();

  const form = useForm<ProductFormData>({
    resolver: zodResolver(productFormSchema),
    defaultValues: {
      ...productFormDefaults,
      ...initialData,
    } as ProductFormData,
    mode: 'onBlur',
    reValidateMode: 'onChange',
  });

  const handleSubmit = form.handleSubmit(async (data) => {
    await onSubmit(data);
  });

  return (
    <Form {...form}>
      <form onSubmit={handleSubmit} className="space-y-6">
        <BasicInfoSection control={form.control} isLoading={isLoading} watch={form.watch} setValue={form.setValue} />

        <PricingSection control={form.control} isLoading={isLoading} watch={form.watch} />

        <InventorySection control={form.control} isLoading={isLoading} watch={form.watch} />

        <CategorizationSection control={form.control} isLoading={isLoading} />

        <MediaSection control={form.control} setValue={form.setValue} isLoading={isLoading} watch={form.watch} />

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 border-t border-gray-200 pt-6 dark:border-gray-700">
          <Button
            type="button"
            variant="outline"
            onClick={() => router.back()}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {initialData ? 'Save Changes' : 'Create Product'}
          </Button>
        </div>
      </form>
    </Form>
  );
}
