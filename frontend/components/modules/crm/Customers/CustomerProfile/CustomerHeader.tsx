'use client';

import { ArrowLeft, Edit, Trash2, MoreVertical } from 'lucide-react';
import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Separator } from '@/components/ui/separator';
import { CustomerAvatar } from './CustomerAvatar';
import type { Customer } from '@/types/customer';

interface CustomerHeaderProps {
  customer: Customer;
  onEdit?: () => void;
  onDelete?: () => void;
}

function getStatusVariant(status: string) {
  switch (status) {
    case 'ACTIVE':
      return 'default';
    case 'INACTIVE':
      return 'secondary';
    case 'SUSPENDED':
      return 'pending';
    case 'BLOCKED':
      return 'destructive';
    default:
      return 'outline';
  }
}

export function CustomerHeader({ customer, onEdit, onDelete }: CustomerHeaderProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/customers">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <span className="text-sm text-muted-foreground">Back to Customers</span>
      </div>

      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <CustomerAvatar
            customer={{ name: customer.displayName, imageUrl: undefined }}
            size="large"
          />
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight">{customer.displayName}</h1>
              <Badge
                variant={
                  getStatusVariant(customer.status) as
                    | 'default'
                    | 'secondary'
                    | 'destructive'
                    | 'outline'
                }
              >
                {customer.status}
              </Badge>
            </div>
            <p className="text-muted-foreground text-sm">
              {customer.customerNumber} · {customer.customerType}
            </p>
            {customer.email && <p className="text-sm text-muted-foreground">{customer.email}</p>}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={onEdit}>
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem className="text-destructive" onClick={onDelete}>
                <Trash2 className="h-4 w-4 mr-2" />
                Delete Customer
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <Separator />
    </div>
  );
}
