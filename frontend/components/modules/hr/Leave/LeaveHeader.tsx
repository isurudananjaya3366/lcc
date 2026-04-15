'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

export function LeaveHeader() {
  const router = useRouter();

  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Leave Management</h1>
        <p className="text-muted-foreground">Manage leave requests, balances, and approvals</p>
      </div>
      <Button onClick={() => router.push('/leave/request')}>
        <Plus className="mr-2 h-4 w-4" />
        Request Leave
      </Button>
    </div>
  );
}
