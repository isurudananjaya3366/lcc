'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Separator } from '@/components/ui/separator';
import { customerKeys } from '@/lib/queryKeys';
import customerService from '@/services/api/customerService';
import type { Customer, CustomerUpdateRequest } from '@/types/customer';

interface EditCustomerModalProps {
  customer: Customer;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function EditCustomerModal({
  customer,
  isOpen,
  onClose,
  onSuccess,
}: EditCustomerModalProps) {
  const queryClient = useQueryClient();

  const [name, setName] = useState(customer.displayName);
  const [type, setType] = useState(customer.customerType);
  const [phone, setPhone] = useState(customer.phone ?? '');
  const [email, setEmail] = useState(customer.email ?? '');
  const [address, setAddress] = useState(customer.addresses?.[0]?.street ?? '');
  const [city, setCity] = useState(customer.addresses?.[0]?.city ?? '');
  const [postalCode, setPostalCode] = useState(customer.addresses?.[0]?.postalCode ?? '');
  const [creditLimit, setCreditLimit] = useState(
    customer.creditLimit?.creditLimit?.toString() ?? '0'
  );
  const [paymentTerms, setPaymentTerms] = useState(customer.creditLimit?.paymentTerms ?? '');

  const mutation = useMutation({
    mutationFn: (data: CustomerUpdateRequest) => customerService.updateCustomer(customer.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: customerKeys.detail(customer.id) });
      queryClient.invalidateQueries({ queryKey: customerKeys.lists() });
      onSuccess?.();
      onClose();
    },
  });

  function handleSave() {
    const data: CustomerUpdateRequest = {
      displayName: name,
      customerType: type,
      phone: phone || undefined,
      email: email || undefined,
    };
    mutation.mutate(data);
  }

  const isValid = name.trim().length >= 2 && name.length <= 200 && phone.trim().length > 0;

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit Customer</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h4 className="text-sm font-medium">Basic Information</h4>
            <div className="space-y-2">
              <Label htmlFor="edit-name">Customer Name *</Label>
              <Input
                id="edit-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                maxLength={200}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-type">Type *</Label>
              <Select value={type} onValueChange={(v) => setType(v as typeof type)}>
                <SelectTrigger id="edit-type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="INDIVIDUAL">Individual</SelectItem>
                  <SelectItem value="BUSINESS">Business</SelectItem>
                  <SelectItem value="WHOLESALER">Wholesaler</SelectItem>
                  <SelectItem value="DISTRIBUTOR">Distributor</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Separator />

          {/* Contact Details */}
          <div className="space-y-4">
            <h4 className="text-sm font-medium">Contact Details</h4>
            <div className="space-y-2">
              <Label htmlFor="edit-phone">Phone *</Label>
              <Input
                id="edit-phone"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+94 XX XXX XXXX"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-email">Email</Label>
              <Input
                id="edit-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          <Separator />

          {/* Address */}
          <div className="space-y-4">
            <h4 className="text-sm font-medium">Address</h4>
            <div className="space-y-2">
              <Label htmlFor="edit-address">Street Address</Label>
              <Input
                id="edit-address"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-city">City</Label>
                <Input id="edit-city" value={city} onChange={(e) => setCity(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-postal">Postal Code</Label>
                <Input
                  id="edit-postal"
                  value={postalCode}
                  onChange={(e) => setPostalCode(e.target.value)}
                />
              </div>
            </div>
          </div>

          <Separator />

          {/* Credit Terms */}
          <div className="space-y-4">
            <h4 className="text-sm font-medium">Credit Terms</h4>
            <div className="space-y-2">
              <Label htmlFor="edit-credit">Credit Limit (₨)</Label>
              <Input
                id="edit-credit"
                type="number"
                min="0"
                value={creditLimit}
                onChange={(e) => setCreditLimit(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-terms">Payment Terms</Label>
              <Select value={paymentTerms} onValueChange={setPaymentTerms}>
                <SelectTrigger id="edit-terms">
                  <SelectValue placeholder="Select terms" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="NET_0">Due on Receipt</SelectItem>
                  <SelectItem value="NET_15">Net 15</SelectItem>
                  <SelectItem value="NET_30">Net 30</SelectItem>
                  <SelectItem value="NET_45">Net 45</SelectItem>
                  <SelectItem value="NET_60">Net 60</SelectItem>
                  <SelectItem value="COD">COD</SelectItem>
                  <SelectItem value="PREPAID">Prepaid</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={!isValid || mutation.isPending}>
            {mutation.isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
