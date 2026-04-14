'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Plus, Trash2, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { salesService } from '@/services/api';
import { salesKeys } from '@/lib/queryKeys';
import { OrderSource, ShippingMethod } from '@/types/sales';

const orderItemSchema = z.object({
  productId: z.string().min(1, 'Product is required'),
  sku: z.string().min(1, 'SKU is required'),
  name: z.string().min(1, 'Name is required'),
  quantity: z.coerce.number().min(1, 'Quantity must be at least 1'),
  unitPrice: z.coerce.number().min(0, 'Price must be positive'),
  discount: z.coerce.number().min(0).default(0),
  discountType: z.enum(['FIXED', 'PERCENTAGE']).default('FIXED'),
  taxRate: z.coerce.number().min(0).default(0),
});

const orderFormSchema = z.object({
  orderSource: z.nativeEnum(OrderSource),
  customerId: z.string().optional(),
  shippingMethod: z.nativeEnum(ShippingMethod).optional(),
  items: z.array(orderItemSchema).min(1, 'At least one item is required'),
  notes: z.string().optional(),
});

type OrderFormData = z.infer<typeof orderFormSchema>;

function formatCurrency(amount: number): string {
  return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

export function NewOrderForm() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    control,
    watch,
    formState: { errors },
  } = useForm<OrderFormData>({
    resolver: zodResolver(orderFormSchema),
    defaultValues: {
      orderSource: OrderSource.POS,
      items: [
        {
          productId: '',
          sku: '',
          name: '',
          quantity: 1,
          unitPrice: 0,
          discount: 0,
          discountType: 'FIXED',
          taxRate: 0,
        },
      ],
      notes: '',
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  });

  const watchItems = watch('items');

  const subtotal = watchItems.reduce((sum, item) => {
    const lineTotal = (item.quantity || 0) * (item.unitPrice || 0);
    return sum + lineTotal;
  }, 0);

  const createMutation = useMutation({
    mutationFn: salesService.createOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salesKeys.all });
      router.push('/orders');
    },
    onError: (err: Error) => {
      setSubmitError(err.message || 'Failed to create order');
    },
  });

  const onSubmit = (data: OrderFormData) => {
    setSubmitError(null);
    createMutation.mutate(data);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/orders">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Create New Order</h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Order Details */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Order Details</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div>
              <Label htmlFor="orderSource">Order Source</Label>
              <Select
                defaultValue={OrderSource.POS}
                onValueChange={(value) => {
                  const event = { target: { name: 'orderSource', value } };
                  register('orderSource').onChange(event);
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select source" />
                </SelectTrigger>
                <SelectContent>
                  {Object.values(OrderSource).map((source) => (
                    <SelectItem key={source} value={source}>
                      {source.replace(/_/g, ' ')}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="customerId">Customer ID</Label>
              <Input id="customerId" placeholder="Enter customer ID" {...register('customerId')} />
            </div>

            <div>
              <Label htmlFor="shippingMethod">Shipping Method</Label>
              <Select
                onValueChange={(value) => {
                  const event = { target: { name: 'shippingMethod', value } };
                  register('shippingMethod').onChange(event);
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select method" />
                </SelectTrigger>
                <SelectContent>
                  {Object.values(ShippingMethod).map((method) => (
                    <SelectItem key={method} value={method}>
                      {method.replace(/_/g, ' ')}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Line Items */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Order Items</CardTitle>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() =>
                append({
                  productId: '',
                  sku: '',
                  name: '',
                  quantity: 1,
                  unitPrice: 0,
                  discount: 0,
                  discountType: 'FIXED',
                  taxRate: 0,
                })
              }
            >
              <Plus className="mr-2 h-4 w-4" />
              Add Item
            </Button>
          </CardHeader>
          <CardContent className="space-y-4">
            {fields.map((field, index) => (
              <div
                key={field.id}
                className="grid grid-cols-12 items-end gap-3 rounded-md border p-3"
              >
                <div className="col-span-3">
                  <Label>Product Name</Label>
                  <Input placeholder="Product name" {...register(`items.${index}.name`)} />
                  {errors.items?.[index]?.name && (
                    <p className="mt-1 text-xs text-red-500">
                      {errors.items[index]?.name?.message}
                    </p>
                  )}
                </div>
                <div className="col-span-2">
                  <Label>SKU</Label>
                  <Input placeholder="SKU" {...register(`items.${index}.sku`)} />
                </div>
                <div className="col-span-1">
                  <Label>Qty</Label>
                  <Input type="number" min={1} {...register(`items.${index}.quantity`)} />
                </div>
                <div className="col-span-2">
                  <Label>Unit Price (₨)</Label>
                  <Input
                    type="number"
                    min={0}
                    step="0.01"
                    {...register(`items.${index}.unitPrice`)}
                  />
                </div>
                <div className="col-span-1">
                  <Label>Discount</Label>
                  <Input
                    type="number"
                    min={0}
                    step="0.01"
                    {...register(`items.${index}.discount`)}
                  />
                </div>
                <div className="col-span-1">
                  <Label>Tax %</Label>
                  <Input
                    type="number"
                    min={0}
                    step="0.01"
                    {...register(`items.${index}.taxRate`)}
                  />
                </div>
                <div className="col-span-1">
                  <Label>Line Total</Label>
                  <p className="py-2 text-sm font-medium">
                    {formatCurrency(
                      (watchItems[index]?.quantity || 0) * (watchItems[index]?.unitPrice || 0)
                    )}
                  </p>
                </div>
                <div className="col-span-1">
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    disabled={fields.length === 1}
                    onClick={() => remove(index)}
                  >
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                </div>
              </div>
            ))}
            {errors.items?.message && (
              <p className="text-sm text-red-500">{errors.items.message}</p>
            )}
          </CardContent>
        </Card>

        {/* Notes */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Notes</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea placeholder="Add order notes..." rows={3} {...register('notes')} />
          </CardContent>
        </Card>

        {/* Summary & Submit */}
        <Card>
          <CardContent className="flex items-center justify-between pt-6">
            <div className="text-lg font-bold">Subtotal: {formatCurrency(subtotal)}</div>
            <div className="flex gap-3">
              <Link href="/orders">
                <Button type="button" variant="outline">
                  Cancel
                </Button>
              </Link>
              {submitError && <p className="self-center text-sm text-red-500">{submitError}</p>}
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? 'Creating...' : 'Create Order'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  );
}
