'use client';

import { useState } from 'react';
import { LeaveHeader } from './LeaveHeader';
import { LeaveBalanceCards } from './LeaveBalanceCards';
import { LeaveRequestsTable } from './LeaveRequestsTable';
import { LeaveCalendar } from './LeaveCalendar';
import { ApprovalModal } from './ApprovalModal';
import { useLeaveRequests, useLeaveBalance, useLeaveCalendar } from '@/hooks/hr/useLeave';
import { Skeleton } from '@/components/ui/skeleton';

export function LeaveDashboard() {
  const [approvalState, setApprovalState] = useState<{
    open: boolean;
    requestId: string;
    action: 'approve' | 'reject';
  }>({ open: false, requestId: '', action: 'approve' });

  const now = new Date();
  const currentMonth = now.getMonth();
  const currentYear = now.getFullYear();

  const { data: requestsData, isLoading: loadingRequests } = useLeaveRequests();
  const { data: balanceData, isLoading: loadingBalance } = useLeaveBalance('me');
  const { data: calendarData } = useLeaveCalendar(
    `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-01`,
    `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${new Date(currentYear, currentMonth + 1, 0).getDate()}`
  );

  const requests = requestsData?.data ?? [];
  const balances = balanceData?.data ?? [];
  const calendarRequests = calendarData?.data ?? [];

  const handleApprove = (id: string) =>
    setApprovalState({ open: true, requestId: id, action: 'approve' });
  const handleReject = (id: string) =>
    setApprovalState({ open: true, requestId: id, action: 'reject' });

  return (
    <div className="space-y-6">
      <LeaveHeader />

      {loadingBalance ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      ) : (
        <LeaveBalanceCards balances={balances} />
      )}

      <div className="grid gap-6 lg:grid-cols-5">
        <div className="lg:col-span-3">
          {loadingRequests ? (
            <Skeleton className="h-64" />
          ) : (
            <LeaveRequestsTable
              requests={requests}
              onApprove={handleApprove}
              onReject={handleReject}
            />
          )}
        </div>
        <div className="lg:col-span-2">
          <LeaveCalendar month={currentMonth} year={currentYear} requests={calendarRequests} />
        </div>
      </div>

      <ApprovalModal
        open={approvalState.open}
        onOpenChange={(open) => setApprovalState((prev) => ({ ...prev, open }))}
        requestId={approvalState.requestId}
        action={approvalState.action}
      />
    </div>
  );
}
