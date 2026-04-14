'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CategoryNameInput } from './CategoryNameInput';
import { ParentCategorySelect } from './ParentCategorySelect';
import { CategoryImageUpload } from './CategoryImageUpload';
import type { ProductCategory } from '@/types/product';

const categorySchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Max 100 characters'),
  slug: z.string().min(1, 'Slug is required').max(120, 'Max 120 characters'),
  description: z.string().max(500, 'Max 500 characters').optional(),
  parentId: z.string().nullable().optional(),
  displayOrder: z.coerce.number().int().min(0).default(0),
  isActive: z.boolean().default(true),
  seoTitle: z.string().max(60, 'Max 60 characters').optional(),
  seoDescription: z.string().max(160, 'Max 160 characters').optional(),
});

type CategoryFormData = z.infer<typeof categorySchema>;

interface CategoryFormProps {
  mode: 'create' | 'edit';
  initialData?: ProductCategory;
  categories: ProductCategory[];
  existingSlugs?: string[];
  onSubmit: (data: CategoryFormData, imageFile: File | null) => void;
  onCancel?: () => void;
  isSubmitting?: boolean;
}

export function CategoryForm({
  mode,
  initialData,
  categories,
  existingSlugs = [],
  onSubmit,
  onCancel,
  isSubmitting,
}: CategoryFormProps) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<CategoryFormData>({
    resolver: zodResolver(categorySchema),
    defaultValues: {
      name: initialData?.name || '',
      slug: initialData?.slug || '',
      description: initialData?.description || '',
      parentId: initialData?.parentId || null,
      displayOrder: initialData?.displayOrder || 0,
      isActive: initialData?.isActive ?? true,
      seoTitle: initialData?.seoMetadata?.title || '',
      seoDescription: initialData?.seoMetadata?.description || '',
    },
  });

  const name = watch('name');
  const slug = watch('slug');
  const parentId = watch('parentId');
  const isActive = watch('isActive');

  // Image state managed outside RHF since it's a File object
  const imageFileRef = { current: null as File | null };

  const handleFormSubmit = (data: CategoryFormData) => {
    onSubmit(data, imageFileRef.current);
  };

  // Filter own slug from uniqueness check when editing
  const filteredSlugs = initialData
    ? existingSlugs.filter((s) => s !== initialData.slug)
    : existingSlugs;

  // Filter self from parent options when editing
  const parentCategories = initialData
    ? categories.filter((c) => c.id !== initialData.id)
    : categories;

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      {/* Basic Info */}
      <Card>
        <CardHeader>
          <CardTitle>Basic Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <CategoryNameInput
            name={name}
            slug={slug}
            onNameChange={(v) => setValue('name', v, { shouldValidate: true })}
            onSlugChange={(v) => setValue('slug', v, { shouldValidate: true })}
            existingSlugs={filteredSlugs}
            error={errors.name?.message || errors.slug?.message}
          />

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              {...register('description')}
              placeholder="Describe this category..."
              rows={3}
            />
            {errors.description && (
              <p className="text-xs text-red-500">{errors.description.message}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Organization */}
      <Card>
        <CardHeader>
          <CardTitle>Organization</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <ParentCategorySelect
            value={parentId || null}
            onChange={(v) => setValue('parentId', v, { shouldValidate: true })}
            currentCategoryId={initialData?.id}
            categories={parentCategories.map((c) => ({
              id: c.id,
              name: c.name,
              parentId: c.parentId || null,
            }))}
          />

          <div className="space-y-2">
            <Label htmlFor="displayOrder">Display Order</Label>
            <Input
              id="displayOrder"
              type="number"
              min={0}
              {...register('displayOrder')}
              className="w-32"
            />
          </div>

          <div className="flex items-center gap-3">
            <Switch
              id="isActive"
              checked={isActive}
              onCheckedChange={(v) => setValue('isActive', v)}
            />
            <Label htmlFor="isActive">Active</Label>
          </div>
        </CardContent>
      </Card>

      {/* Image */}
      <Card>
        <CardHeader>
          <CardTitle>Image</CardTitle>
        </CardHeader>
        <CardContent>
          <CategoryImageUpload
            imageUrl={initialData?.imageUrl || null}
            onImageChange={(file) => {
              imageFileRef.current = file;
            }}
          />
        </CardContent>
      </Card>

      {/* SEO */}
      <Card>
        <CardHeader>
          <CardTitle>SEO</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="seoTitle">Meta Title</Label>
            <Input
              id="seoTitle"
              {...register('seoTitle')}
              placeholder="Category page title"
              maxLength={60}
            />
            <p className="text-xs text-muted-foreground">
              {(watch('seoTitle') || '').length}/60 characters
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="seoDescription">Meta Description</Label>
            <Textarea
              id="seoDescription"
              {...register('seoDescription')}
              placeholder="Brief description for search engines..."
              rows={2}
              maxLength={160}
            />
            <p className="text-xs text-muted-foreground">
              {(watch('seoDescription') || '').length}/160 characters
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex items-center justify-end gap-3">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting
            ? mode === 'create'
              ? 'Creating...'
              : 'Saving...'
            : mode === 'create'
              ? 'Create Category'
              : 'Save Changes'}
        </Button>
      </div>
    </form>
  );
}
