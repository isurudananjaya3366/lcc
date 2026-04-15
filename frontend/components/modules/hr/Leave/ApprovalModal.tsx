'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { LeaveStatusBadge } from './LeaveStatusBadge';
import { useApproveLeaveRequest, useRejectLeaveRequest } from '@/hooks/hr/useLeave';
import type { LeaveRequest } from '@/types/hr';

interface ApprovalModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  requestId: string;
  action: 'approve' | 'reject';
  request?: LeaveRequest | null;
}

function formatDate(d?: string): string {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('en-LK', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function calculateWorkingDays(start: string, end: string): number {
  if (!start || !end) return 0;
  const s = new Date(start);
  const e = new Date(end);
  if (e < s) return 0;
  let count = 0;
  const c = new Date(s);
  while (c <= e) {
    if (c.getDay() !== 0 && c.getDay() !== 6) count++;
    c.setDate(c.getDate() + 1);
  }
  return count;
}

export function ApprovalModal({
  open,
  onOpenChange,
  requestId,
  action,
  request,
}: ApprovalModalProps) {
  const [comment, setComment] = useState('');
  const approveMutation = useApproveLeaveRequest();
  const rejectMutation = useRejectLeaveRequest();

  const isReject = action === 'reject';
  const isPending = approveMutation.isPending || rejectMutation.isPending;

  const handleSubmit = () => {
    if (isReject && comment.length < 20) return;

    if (isReject) {
      rejectMutation.mutate(
        { id: requestId, reason: comment },
        {
          onSuccess: () => {
            onOpenChange(false);
            setComment('');
          },
        }
      );
    } else {
      approveMutation.mutate(
        { id: requestId, comment: comment || undefined },
        {
          onSuccess: () => {
            onOpenChange(false);
            setComment('');
          },
        }
      );
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{isReject ? 'Reject Leave Request' : 'Approve Leave Request'}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          {request && (
            <div className="rounded-md border p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Request Details</span>
                <LeaveStatusBadge status={request.status} />
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <p className="text-muted-foreground">Employee</p>
                  <p className="font-medium">{request.employeeId}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Leave Type</p>
                  <Badge variant="outline">{request.leaveType}</Badge>
                </div>
                <div>
                  <p className="text-muted-foreground">Period</p>
                  <p className="font-medium">
                    {formatDate(request.startDate)} — {formatDate(request.endDate)}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Duration</p>
                  <p className="font-medium">
                    {calculateWorkingDays(request.startDate, request.endDate)} working days
                  </p>
                </div>
              </div>
              {request.reason && (
                <div className="text-sm">
                  <p className="text-muted-foreground">Reason</p>
                  <p className="mt-1">{request.reason}</p>
                </div>
              )}
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="comment">
              {isReject ? 'Rejection Reason *' : 'Comment (optional)'}
            </Label>
            <Textarea
              id="comment"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder={
                isReject ? 'Enter reason for rejection (minimum 20 characters)' : 'Add a comment...'
              }
              maxLength={500}
            />
            {isReject && comment.length > 0 && comment.length < 20 && (
              <p className="text-xs text-destructive">
                Reason must be at least 20 characters ({comment.length}/20)
              </p>
            )}
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            variant={isReject ? 'destructive' : 'default'}
            onClick={handleSubmit}
            disabled={isPending || (isReject && comment.length < 20)}
          >
            {isPending ? 'Processing...' : isReject ? 'Reject' : 'Approve'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
