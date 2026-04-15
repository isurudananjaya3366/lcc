'use client';

import { useForm, Controller, type Resolver } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  shippingFormSchema,
  serviceLevels,
  type ShippingFormValues,
} from '@/lib/validations/shipping';
import { CarrierSelection } from './CarrierSelection';
import { TrackingInput } from './TrackingInput';
import { PrintLabelButton } from './PrintLabelButton';
import type { OrderAddress } from '@/types/sales';

interface ShippingLabelModalProps {
  isOpen: boolean;
  onClose: () => void;
  orderNumber: string;
  shippingAddress?: OrderAddress;
  itemCount: number;
  isSubmitting?: boolean;
  onSubmit: (data: ShippingFormValues) => void;
}

export function ShippingLabelModal({
  isOpen,
  onClose,
  orderNumber,
  shippingAddress,
  itemCount,
  isSubmitting,
  onSubmit,
}: ShippingLabelModalProps) {
  const {
    control,
    handleSubmit,
    watch,
    formState: { errors },
    reset,
  } = useForm<ShippingFormValues>({
    resolver: zodResolver(shippingFormSchema) as Resolver<ShippingFormValues>,
    defaultValues: {
      carrier: '',
      serviceLevel: 'STANDARD',
      trackingNumber: '',
      shippingNotes: '',
      notifyCustomer: true,
    },
  });

  const selectedCarrier = watch('carrier');

  const handleClose = () => {
    reset();
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && handleClose()}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Ship Order — {orderNumber}</DialogTitle>
        </DialogHeader>

        {/* Shipping Address */}
        {shippingAddress && (
          <div className="rounded-md border bg-gray-50 p-3 text-sm dark:bg-gray-800">
            <p className="mb-1 font-medium">Ship To</p>
            <p>
              {shippingAddress.firstName} {shippingAddress.lastName}
            </p>
            {shippingAddress.companyName && <p>{shippingAddress.companyName}</p>}
            <p>{shippingAddress.street}</p>
            {shippingAddress.street2 && <p>{shippingAddress.street2}</p>}
            <p>
              {shippingAddress.city}, {shippingAddress.state} {shippingAddress.postalCode}
            </p>
            <p>{shippingAddress.country}</p>
            <p className="mt-1 text-gray-500">{itemCount} item(s)</p>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Controller
            name="carrier"
            control={control}
            render={({ field }) => (
              <CarrierSelection
                value={field.value}
                onChange={field.onChange}
                error={errors.carrier?.message}
              />
            )}
          />

          <Controller
            name="serviceLevel"
            control={control}
            render={({ field }) => (
              <div className="space-y-1.5">
                <Label>Service Level *</Label>
                <Select value={field.value} onValueChange={field.onChange}>
                  <SelectTrigger className={errors.serviceLevel ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select level" />
                  </SelectTrigger>
                  <SelectContent>
                    {serviceLevels.map((level) => (
                      <SelectItem key={level.value} value={level.value}>
                        {level.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.serviceLevel && (
                  <p className="text-xs text-red-500">{errors.serviceLevel.message}</p>
                )}
              </div>
            )}
          />

          <Controller
            name="trackingNumber"
            control={control}
            render={({ field }) => (
              <TrackingInput
                value={field.value}
                onChange={field.onChange}
                carrier={selectedCarrier}
                error={errors.trackingNumber?.message}
              />
            )}
          />

          <Controller
            name="shippingNotes"
            control={control}
            render={({ field }) => (
              <div className="space-y-1.5">
                <Label>Shipping Notes</Label>
                <Textarea
                  value={field.value ?? ''}
                  onChange={field.onChange}
                  placeholder="Add shipping notes..."
                  rows={2}
                  maxLength={500}
                />
              </div>
            )}
          />

          <Controller
            name="notifyCustomer"
            control={control}
            render={({ field }) => (
              <div className="flex items-center gap-2">
                <Checkbox
                  id="notifyCustomer"
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
                <Label htmlFor="notifyCustomer" className="text-sm font-normal">
                  Send shipping notification to customer
                </Label>
              </div>
            )}
          />

          <DialogFooter className="gap-2">
            <PrintLabelButton disabled={!selectedCarrier} />
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Shipping...' : 'Mark as Shipped'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
