'use client';

import { useRouter } from 'next/navigation';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ArrowLeft } from 'lucide-react';
import { LeaveTypeSelect } from './LeaveTypeSelect';
import { useSubmitLeaveRequest } from '@/hooks/hr/useLeave';
import { leaveRequestSchema, type LeaveRequestFormValues } from '@/lib/validations/leave';
import { useMemo } from 'react';

function calculateWorkingDays(start: string, end: string): number {
  if (!start || !end) return 0;
  const startDate = new Date(start);
  const endDate = new Date(end);
  if (endDate < startDate) return 0;
  let count = 0;
  const current = new Date(startDate);
  while (current <= endDate) {
    const day = current.getDay();
    if (day !== 0 && day !== 6) count++;
    current.setDate(current.getDate() + 1);
  }
  return count;
}

export function LeaveRequestForm() {
  const router = useRouter();
  const submitMutation = useSubmitLeaveRequest();

  const {
    register,
    handleSubmit,
    control,
    watch,
    formState: { errors },
  } = useForm<LeaveRequestFormValues>({
    resolver: zodResolver(leaveRequestSchema),
    defaultValues: {
      leaveType: '',
      startDate: '',
      endDate: '',
      reason: '',
    },
  });

  const startDate = watch('startDate');
  const endDate = watch('endDate');
  const reason = watch('reason');

  const workingDays = useMemo(() => calculateWorkingDays(startDate, endDate), [startDate, endDate]);

  const onSubmit = (data: LeaveRequestFormValues) => {
    submitMutation.mutate(
      {
        leaveType: data.leaveType,
        startDate: data.startDate,
        endDate: data.endDate,
        reason: data.reason || undefined,
      },
      {
        onSuccess: () => router.push('/leave'),
      }
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Request Leave</h1>
          <p className="text-muted-foreground">Submit a new leave request for approval</p>
        </div>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Leave Details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="leaveType">Leave Type *</Label>
              <Controller
                name="leaveType"
                control={control}
                render={({ field }) => (
                  <LeaveTypeSelect value={field.value} onChange={field.onChange} />
                )}
              />
              {errors.leaveType && (
                <p className="text-xs text-destructive">{errors.leaveType.message}</p>
              )}
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="startDate">Start Date *</Label>
                <Input id="startDate" type="date" {...register('startDate')} />
                {errors.startDate && (
                  <p className="text-xs text-destructive">{errors.startDate.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="endDate">End Date *</Label>
                <Input id="endDate" type="date" {...register('endDate')} />
                {errors.endDate && (
                  <p className="text-xs text-destructive">{errors.endDate.message}</p>
                )}
              </div>
            </div>

            {workingDays > 0 && (
              <div className="rounded-md bg-muted px-4 py-2 text-sm">
                Working days: <strong>{workingDays}</strong>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="reason">
                Reason{' '}
                <span className="text-xs text-muted-foreground">(optional, 10-500 characters)</span>
              </Label>
              <Textarea
                id="reason"
                {...register('reason')}
                placeholder="Provide a reason for your leave request..."
                maxLength={500}
                rows={4}
              />
              <div className="flex justify-between">
                {errors.reason && (
                  <p className="text-xs text-destructive">{errors.reason.message}</p>
                )}
                <p className="ml-auto text-xs text-muted-foreground">{reason?.length ?? 0}/500</p>
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <Button type="submit" disabled={submitMutation.isPending}>
                {submitMutation.isPending ? 'Submitting...' : 'Submit Request'}
              </Button>
              <Button type="button" variant="outline" onClick={() => router.back()}>
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
