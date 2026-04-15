'use client';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MoreHorizontal, CheckCircle, XCircle, Ban } from 'lucide-react';
import { LeaveStatusBadge } from './LeaveStatusBadge';
import type { LeaveRequest } from '@/types/hr';

interface LeaveRequestsTableProps {
  requests: LeaveRequest[];
  onApprove?: (id: string) => void;
  onReject?: (id: string) => void;
  onCancel?: (id: string) => void;
}

export function LeaveRequestsTable({
  requests,
  onApprove,
  onReject,
  onCancel,
}: LeaveRequestsTableProps) {
  if (requests.length === 0) {
    return (
      <div className="flex min-h-[200px] items-center justify-center text-muted-foreground">
        No leave requests found.
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[200px]">Employee</TableHead>
            <TableHead className="w-[100px]">Type</TableHead>
            <TableHead className="w-[100px]">Start Date</TableHead>
            <TableHead className="w-[100px]">End Date</TableHead>
            <TableHead className="w-[60px]">Days</TableHead>
            <TableHead className="w-[100px]">Status</TableHead>
            <TableHead className="w-[120px]" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {requests.map((request) => (
            <TableRow key={request.id}>
              <TableCell className="font-medium">{request.employeeId}</TableCell>
              <TableCell>{request.leaveType.replace('_', ' ')}</TableCell>
              <TableCell>
                {new Date(request.startDate).toLocaleDateString('en-LK', {
                  day: '2-digit',
                  month: 'short',
                  year: 'numeric',
                })}
              </TableCell>
              <TableCell>
                {new Date(request.endDate).toLocaleDateString('en-LK', {
                  day: '2-digit',
                  month: 'short',
                  year: 'numeric',
                })}
              </TableCell>
              <TableCell>{request.days}</TableCell>
              <TableCell>
                <LeaveStatusBadge status={request.status} />
              </TableCell>
              <TableCell>
                {request.status === 'PENDING' && (
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      {onApprove && (
                        <DropdownMenuItem onClick={() => onApprove(request.id)}>
                          <CheckCircle className="mr-2 h-4 w-4 text-green-500" />
                          Approve
                        </DropdownMenuItem>
                      )}
                      {onReject && (
                        <DropdownMenuItem onClick={() => onReject(request.id)}>
                          <XCircle className="mr-2 h-4 w-4 text-red-500" />
                          Reject
                        </DropdownMenuItem>
                      )}
                      {onCancel && (
                        <DropdownMenuItem onClick={() => onCancel(request.id)}>
                          <Ban className="mr-2 h-4 w-4" />
                          Cancel
                        </DropdownMenuItem>
                      )}
                    </DropdownMenuContent>
                  </DropdownMenu>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
