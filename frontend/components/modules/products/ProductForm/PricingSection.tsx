'use client';

import { type Control, type UseFormWatch } from 'react-hook-form';
import type { ProductFormData } from '@/lib/validations/product';
import { TAX_CATEGORIES } from '@/lib/tax';
import {
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
} from '@/components/ui/form';
import { PriceInput } from '@/components/ui/price-input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface PricingSectionProps {
  control: Control<ProductFormData>;
  isLoading?: boolean;
  watch: UseFormWatch<ProductFormData>;
}

export function PricingSection({ control, isLoading = false, watch }: PricingSectionProps) {
  const costPrice = watch('cost_price') ?? 0;
  const sellingPrice = watch('selling_price') ?? 0;
  const taxCategoryId = watch('tax_category_id');

  const profit = sellingPrice - costPrice;
  const margin = sellingPrice > 0 ? (profit / sellingPrice) * 100 : 0;
  const markup = costPrice > 0 ? (profit / costPrice) * 100 : 0;

  const taxCategory = TAX_CATEGORIES.find((t) => t.id === taxCategoryId);
  const taxRate = taxCategory?.rate ?? 0;
  const taxAmount = taxRate !== null ? sellingPrice * (taxRate / 100) : 0;
  const finalPrice = sellingPrice + taxAmount;

  const getMarginColor = () => {
    if (margin > 20) return 'text-green-600 dark:text-green-400';
    if (margin > 10) return 'text-green-500 dark:text-green-400';
    if (margin > 0) return 'text-amber-600 dark:text-amber-400';
    if (margin < 0) return 'text-red-600 dark:text-red-400';
    return 'text-gray-500 dark:text-gray-400';
  };

  const formatLKR = (value: number) =>
    new Intl.NumberFormat('en-LK', {
      style: 'currency',
      currency: 'LKR',
      minimumFractionDigits: 2,
    }).format(value);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Pricing</CardTitle>
        <CardDescription>Set product pricing and margins</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          {/* Cost Price */}
          <FormField
            control={control}
            name="cost_price"
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>Cost Price</FormLabel>
                <FormControl>
                  <PriceInput
                    value={field.value}
                    onChange={field.onChange}
                    onBlur={field.onBlur}
                    disabled={isLoading}
                    error={!!fieldState.error}
                    placeholder="0.00"
                  />
                </FormControl>
                <FormDescription>Your cost to acquire/produce this product</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Selling Price */}
          <FormField
            control={control}
            name="selling_price"
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>Selling Price</FormLabel>
                <FormControl>
                  <PriceInput
                    value={field.value}
                    onChange={field.onChange}
                    onBlur={field.onBlur}
                    disabled={isLoading}
                    error={!!fieldState.error}
                    placeholder="0.00"
                  />
                </FormControl>
                <FormDescription>Price customers will pay (before tax)</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Margin / Markup */}
        {sellingPrice > 0 && (
          <p className={`text-sm font-medium ${getMarginColor()}`}>
            Profit Margin: {margin.toFixed(1)}% &middot; Markup: {markup.toFixed(1)}%
          </p>
        )}

        {/* Tax Category */}
        <FormField
          control={control}
          name="tax_category_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Tax Category</FormLabel>
              <Select onValueChange={field.onChange} value={field.value} disabled={isLoading}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select tax category" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {TAX_CATEGORIES.map((cat) => (
                    <SelectItem key={cat.id} value={cat.id}>
                      <span className="flex items-center gap-2">
                        {cat.name} {cat.rate !== null ? `— ${cat.rate}%` : ''}
                        <span className="text-xs text-muted-foreground">{cat.description}</span>
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormDescription>Select applicable tax rate</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Price Summary */}
        {sellingPrice > 0 && (
          <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/50">
            <h4 className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
              Price Summary
            </h4>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Cost Price</span>
                <span className="tabular-nums">{formatLKR(costPrice)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500 dark:text-gray-400">Selling Price</span>
                <span className="tabular-nums">{formatLKR(sellingPrice)}</span>
              </div>
              {taxRate > 0 && (
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Tax ({taxRate}%)</span>
                  <span className="tabular-nums">{formatLKR(taxAmount)}</span>
                </div>
              )}
              <div className="border-t border-gray-200 pt-1 dark:border-gray-700">
                <div className="flex justify-between font-medium">
                  <span>Final Price</span>
                  <span className="tabular-nums">{formatLKR(finalPrice)}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
