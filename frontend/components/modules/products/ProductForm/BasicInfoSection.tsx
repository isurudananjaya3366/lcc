'use client';

import { useState, useEffect, useCallback } from 'react';
import { type Control, type UseFormWatch, type UseFormSetValue } from 'react-hook-form';
import { RefreshCw } from 'lucide-react';

import type { ProductFormData } from '@/lib/validations/product';
import { generateSKU } from '@/lib/sku';
import {
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { DescriptionEditor } from './DescriptionEditor';

interface BasicInfoSectionProps {
  control: Control<ProductFormData>;
  isLoading?: boolean;
  watch: UseFormWatch<ProductFormData>;
  setValue: UseFormSetValue<ProductFormData>;
}

export function BasicInfoSection({
  control,
  isLoading = false,
  watch,
  setValue,
}: BasicInfoSectionProps) {
  const [isSkuManual, setIsSkuManual] = useState(false);
  const name = watch('name');

  // Auto-generate SKU when name changes (unless user has manually edited)
  useEffect(() => {
    if (!isSkuManual && name && name.length >= 2) {
      const sku = generateSKU(name);
      setValue('sku', sku, { shouldValidate: true });
    }
  }, [name, isSkuManual, setValue]);

  const handleGenerateSKU = useCallback(() => {
    const currentName = watch('name');
    const sku = generateSKU(currentName || '');
    setValue('sku', sku, { shouldValidate: true });
    setIsSkuManual(false);
  }, [watch, setValue]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Basic Information</CardTitle>
        <CardDescription>Core product identification details</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Product Name */}
        <FormField
          control={control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Product Name</FormLabel>
              <FormControl>
                <Input
                  placeholder="Enter product name"
                  disabled={isLoading}
                  {...field}
                />
              </FormControl>
              <FormDescription>The name customers will see</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* SKU */}
        <FormField
          control={control}
          name="sku"
          render={({ field }) => (
            <FormItem>
              <FormLabel>SKU (Stock Keeping Unit)</FormLabel>
              <div className="flex gap-2">
                <FormControl>
                  <Input
                    placeholder="e.g., PROD-12345"
                    disabled={isLoading}
                    {...field}
                    onChange={(e) => {
                      setIsSkuManual(true);
                      field.onChange(e);
                    }}
                  />
                </FormControl>
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={handleGenerateSKU}
                  disabled={isLoading}
                  title="Generate SKU"
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </div>
              <FormDescription>Unique product identifier</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Description */}
        <FormField
          control={control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Product Description</FormLabel>
              <FormControl>
                <DescriptionEditor
                  value={field.value ?? ''}
                  onChange={field.onChange}
                  disabled={isLoading}
                />
              </FormControl>
              <FormDescription>Optional — Detailed product information</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      </CardContent>
    </Card>
  );
}
