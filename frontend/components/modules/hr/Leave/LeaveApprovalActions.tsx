'use client';

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Check, X, MoreHorizontal, Info } from 'lucide-react';
import type { LeaveRequest } from '@/types/hr';

interface LeaveApprovalActionsProps {
  request: LeaveRequest;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  onCancel?: (id: string) => void;
  onRequestInfo?: (id: string) => void;
  isPending?: boolean;
}

export function LeaveApprovalActions({
  request,
  onApprove,
  onReject,
  onCancel,
  onRequestInfo,
  isPending = false,
}: LeaveApprovalActionsProps) {
  const isPendingStatus = request.status === 'PENDING';

  if (!isPendingStatus) {
    return null;
  }

  return (
    <div className="flex items-center gap-1">
      <Button
        variant="ghost"
        size="sm"
        className="text-green-600 hover:text-green-700 hover:bg-green-50"
        onClick={() => onApprove(request.id)}
        disabled={isPending}
      >
        <Check className="mr-1 h-4 w-4" />
        Approve
      </Button>
      <Button
        variant="ghost"
        size="sm"
        className="text-red-600 hover:text-red-700 hover:bg-red-50"
        onClick={() => onReject(request.id)}
        disabled={isPending}
      >
        <X className="mr-1 h-4 w-4" />
        Reject
      </Button>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" className="h-8 w-8" disabled={isPending}>
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          {onRequestInfo && (
            <>
              <DropdownMenuItem onClick={() => onRequestInfo(request.id)}>
                <Info className="mr-2 h-4 w-4" />
                Request More Info
              </DropdownMenuItem>
              <DropdownMenuSeparator />
            </>
          )}
          {onCancel && (
            <DropdownMenuItem onClick={() => onCancel(request.id)} className="text-destructive">
              <X className="mr-2 h-4 w-4" />
              Cancel Request
            </DropdownMenuItem>
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
