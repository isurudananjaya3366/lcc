'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { MoreVertical, Eye, Edit, CreditCard, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import customerService from '@/services/api/customerService';
import { customerKeys } from '@/lib/queryKeys';
import type { Customer } from '@/types/customer';

interface CustomerActionsCellProps {
  customer: Customer;
}

export function CustomerActionsCell({ customer }: CustomerActionsCellProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [deleteOpen, setDeleteOpen] = useState(false);

  const deleteMutation = useMutation({
    mutationFn: () => customerService.deleteCustomer(customer.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: customerKeys.all() });
      setDeleteOpen(false);
    },
  });

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <MoreVertical className="h-4 w-4" />
            <span className="sr-only">Actions</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={() => router.push(`/customers/${customer.id}`)}>
            <Eye className="mr-2 h-4 w-4" />
            View Details
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => router.push(`/customers/${customer.id}?edit=true`)}>
            <Edit className="mr-2 h-4 w-4" />
            Edit Customer
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => router.push(`/customers/${customer.id}?tab=credit`)}>
            <CreditCard className="mr-2 h-4 w-4" />
            Adjust Credit
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem
            className="text-red-600 focus:text-red-600"
            onClick={() => setDeleteOpen(true)}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Delete Customer
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Customer?</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete &ldquo;{customer.displayName}&rdquo;? This action
              cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => deleteMutation.mutate()}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? 'Deleting...' : 'Delete Customer'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
