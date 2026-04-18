'use client';

import { useState, useEffect, useCallback } from 'react';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { AddressGrid } from './AddressGrid';
import { AddressFormModal } from './AddressFormModal';
import { DeleteConfirmation } from './DeleteConfirmation';
import { AddressesHeader } from './AddressesHeader';
import {
  getAddresses,
  createAddress,
  updateAddress,
  deleteAddress,
  setDefaultAddress,
} from '@/services/storefront/portalService';
import type { PortalAddress } from '@/types/storefront/portal.types';
import type { AddressFormValues } from '@/lib/validations/addressSchema';

export function AddressesPage() {
  const [addresses, setAddresses] = useState<PortalAddress[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingAddress, setEditingAddress] = useState<PortalAddress | null>(
    null
  );
  const [deletingAddress, setDeletingAddress] = useState<PortalAddress | null>(
    null
  );
  const [isPending, setIsPending] = useState(false);

  const fetchAddresses = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getAddresses();
      setAddresses(data);
    } catch {
      toast.error('Failed to load addresses');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAddresses();
  }, [fetchAddresses]);

  const handleAdd = () => {
    setEditingAddress(null);
    setShowForm(true);
  };

  const handleEdit = (address: PortalAddress) => {
    setEditingAddress(address);
    setShowForm(true);
  };

  const handleSave = async (data: AddressFormValues) => {
    try {
      setIsPending(true);
      if (editingAddress) {
        await updateAddress(editingAddress.id, data);
        toast.success('Address updated successfully');
      } else {
        await createAddress({ ...data, country: 'Sri Lanka' });
        toast.success('Address added successfully');
      }
      setShowForm(false);
      setEditingAddress(null);
      await fetchAddresses();
    } catch {
      toast.error('Failed to save address');
    } finally {
      setIsPending(false);
    }
  };

  const handleDelete = async () => {
    if (!deletingAddress) return;
    try {
      setIsPending(true);
      await deleteAddress(deletingAddress.id);
      toast.success('Address deleted successfully');
      setDeletingAddress(null);
      await fetchAddresses();
    } catch {
      toast.error('Failed to delete address');
    } finally {
      setIsPending(false);
    }
  };

  const handleSetDefault = async (id: string) => {
    try {
      await setDefaultAddress(id);
      toast.success('Default address updated');
      await fetchAddresses();
    } catch {
      toast.error('Failed to set default address');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <AddressesHeader onAdd={handleAdd} />

      <AddressGrid
        addresses={addresses}
        onEdit={handleEdit}
        onDelete={setDeletingAddress}
        onSetDefault={handleSetDefault}
        onAdd={handleAdd}
      />

      <AddressFormModal
        open={showForm}
        onOpenChange={(open) => {
          setShowForm(open);
          if (!open) setEditingAddress(null);
        }}
        address={editingAddress}
        onSave={handleSave}
        isPending={isPending}
      />

      <DeleteConfirmation
        open={!!deletingAddress}
        onOpenChange={(open) => {
          if (!open) setDeletingAddress(null);
        }}
        onConfirm={handleDelete}
        addressLabel={
          deletingAddress?.label ??
          (`${deletingAddress?.firstName ?? ''} ${deletingAddress?.lastName ?? ''}`.trim() ||
          undefined)
        }
      />
    </div>
  );
}
