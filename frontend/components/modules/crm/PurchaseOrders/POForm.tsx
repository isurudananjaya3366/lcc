'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { useCreatePurchaseOrder } from '@/hooks/crm/usePurchaseOrders';
import { POLineItemEditor, type LineItem } from './POLineItemEditor';

export function POForm() {
  const router = useRouter();
  const createPO = useCreatePurchaseOrder();

  const [vendorId, setVendorId] = useState('');
  const [orderDate, setOrderDate] = useState(new Date().toISOString().split('T')[0] ?? '');
  const [expectedDate, setExpectedDate] = useState('');
  const [items, setItems] = useState<LineItem[]>([{ productId: '', quantity: 1, unitCost: 0 }]);
  const [shipping, setShipping] = useState(0);
  const [tax, setTax] = useState(0);
  const [notes, setNotes] = useState('');
  const [terms, setTerms] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const subtotal = items.reduce((sum, item) => sum + item.quantity * item.unitCost, 0);
  const total = subtotal + shipping + tax;

  function validate(): boolean {
    const errs: Record<string, string> = {};
    if (!vendorId.trim()) errs.vendorId = 'Vendor is required';
    if (!orderDate) errs.orderDate = 'Order date is required';
    if (items.length === 0) errs.items = 'At least one item is required';
    const invalidItems = items.some((i) => !i.productId.trim() || i.quantity < 1);
    if (invalidItems) errs.items = 'All items must have a product ID and quantity ≥ 1';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validate()) return;

    createPO.mutate(
      {
        vendorId,
        orderDate,
        expectedDate: expectedDate || undefined,
        status: 'DRAFT',
        items: items.map((i) => ({
          productId: i.productId,
          variantId: i.variantId,
          quantity: i.quantity,
          unitCost: i.unitCost,
          total: i.quantity * i.unitCost,
        })),
        subtotal,
        tax,
        shipping,
        total,
        notes: notes || undefined,
        terms: terms || undefined,
        createdBy: '',
      },
      {
        onSuccess: () => router.push('/purchase-orders'),
      }
    );
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/purchase-orders">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <h1 className="text-2xl font-bold tracking-tight">Create Purchase Order</h1>
      </div>

      <form onSubmit={handleSubmit}>
        <Card>
          <CardContent className="p-6 space-y-6">
            {/* Order Details */}
            <div className="space-y-4">
              <h3 className="text-sm font-medium">Order Details</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="vendorId">Vendor ID *</Label>
                  <Input
                    id="vendorId"
                    value={vendorId}
                    onChange={(e) => setVendorId(e.target.value)}
                    placeholder="Enter vendor ID"
                  />
                  {errors.vendorId && <p className="text-xs text-destructive">{errors.vendorId}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="orderDate">Order Date *</Label>
                  <Input
                    id="orderDate"
                    type="date"
                    value={orderDate}
                    onChange={(e) => setOrderDate(e.target.value)}
                  />
                  {errors.orderDate && (
                    <p className="text-xs text-destructive">{errors.orderDate}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="expectedDate">Expected Delivery</Label>
                  <Input
                    id="expectedDate"
                    type="date"
                    value={expectedDate}
                    onChange={(e) => setExpectedDate(e.target.value)}
                  />
                </div>
              </div>
            </div>

            <Separator />

            {/* Line Items */}
            <POLineItemEditor items={items} onChange={setItems} error={errors.items} />

            <Separator />

            {/* Costs */}
            <div className="space-y-4">
              <h3 className="text-sm font-medium">Additional Costs</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="shipping">Shipping (₨)</Label>
                  <Input
                    id="shipping"
                    type="number"
                    min={0}
                    step={0.01}
                    value={shipping}
                    onChange={(e) => setShipping(Number(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="tax">Tax (₨)</Label>
                  <Input
                    id="tax"
                    type="number"
                    min={0}
                    step={0.01}
                    value={tax}
                    onChange={(e) => setTax(Number(e.target.value))}
                  />
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-muted-foreground">
                  Subtotal: ₨ {subtotal.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
                </p>
                <p className="text-lg font-bold">
                  Total: ₨ {total.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
                </p>
              </div>
            </div>

            <Separator />

            {/* Notes & Terms */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Internal notes..."
                  maxLength={2000}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="terms">Terms & Conditions</Label>
                <Textarea
                  id="terms"
                  value={terms}
                  onChange={(e) => setTerms(e.target.value)}
                  placeholder="Payment terms, delivery conditions..."
                  maxLength={2000}
                />
              </div>
            </div>

            <Separator />

            <div className="flex items-center justify-end gap-3">
              <Button type="button" variant="outline" asChild>
                <Link href="/purchase-orders">Cancel</Link>
              </Button>
              <Button type="submit" disabled={createPO.isPending}>
                {createPO.isPending ? 'Creating...' : 'Create Purchase Order'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  );
}
