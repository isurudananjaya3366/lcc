'use client';

import { type Control } from 'react-hook-form';
import type { ProductFormData } from '@/lib/validations/product';
import {
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
} from '@/components/ui/form';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { CategoryMultiSelect } from './CategoryMultiSelect';
import { TagsInput } from './TagsInput';

interface CategorizationSectionProps {
  control: Control<ProductFormData>;
  isLoading?: boolean;
}

export function CategorizationSection({ control, isLoading = false }: CategorizationSectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Categorization</CardTitle>
        <CardDescription>Organize your product with categories and tags</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Categories */}
        <FormField
          control={control}
          name="category_ids"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Categories</FormLabel>
              <FormControl>
                <CategoryMultiSelect
                  value={field.value ?? []}
                  onChange={field.onChange}
                  disabled={isLoading}
                />
              </FormControl>
              <FormDescription>Select categories for this product</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Tags */}
        <FormField
          control={control}
          name="tags"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Tags</FormLabel>
              <FormControl>
                <TagsInput
                  value={field.value ?? []}
                  onChange={field.onChange}
                  disabled={isLoading}
                  placeholder="Add tags..."
                />
              </FormControl>
              <FormDescription>Add tags for better searchability (max 20)</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      </CardContent>
    </Card>
  );
}
