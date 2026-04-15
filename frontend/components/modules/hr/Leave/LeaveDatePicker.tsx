'use client';

import { useMemo } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import type { LeaveBalance } from '@/types/hr';

interface LeaveDatePickerProps {
  startDate: string;
  endDate: string;
  onStartDateChange: (date: string) => void;
  onEndDateChange: (date: string) => void;
  halfDay?: boolean;
  onHalfDayChange?: (val: boolean) => void;
  halfDayPeriod?: string;
  onHalfDayPeriodChange?: (val: string) => void;
  leaveBalance?: LeaveBalance;
  errors?: { startDate?: { message?: string }; endDate?: { message?: string } };
}

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

const quickDurations = [
  { label: '1 Day', days: 0 },
  { label: '3 Days', days: 2 },
  { label: '1 Week', days: 4 },
  { label: '2 Weeks', days: 9 },
];

export function LeaveDatePicker({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  halfDay,
  onHalfDayChange,
  halfDayPeriod,
  onHalfDayPeriodChange,
  leaveBalance,
  errors,
}: LeaveDatePickerProps) {
  const today = new Date().toISOString().slice(0, 10);

  const workingDays = useMemo(
    () => (halfDay ? 0.5 : calculateWorkingDays(startDate, endDate)),
    [startDate, endDate, halfDay]
  );

  const validationError = useMemo(() => {
    if (startDate && endDate && startDate > endDate) return 'End date must be after start date';
    if (leaveBalance && workingDays > (leaveBalance.remaining ?? Infinity))
      return `Exceeds available balance (${leaveBalance.remaining} days remaining)`;
    return null;
  }, [startDate, endDate, leaveBalance, workingDays]);

  const applyQuickDuration = (businessDays: number) => {
    if (!startDate) {
      onStartDateChange(today);
    }
    const base = new Date(startDate || today);
    let added = 0;
    const d = new Date(base);
    while (added < businessDays) {
      d.setDate(d.getDate() + 1);
      if (d.getDay() !== 0 && d.getDay() !== 6) added++;
    }
    onEndDateChange(d.toISOString().slice(0, 10));
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {quickDurations.map((qd) => (
          <Button
            key={qd.label}
            type="button"
            variant="outline"
            size="sm"
            className="text-xs"
            onClick={() => applyQuickDuration(qd.days)}
          >
            {qd.label}
          </Button>
        ))}
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="leave-start">Start Date *</Label>
          <Input
            id="leave-start"
            type="date"
            value={startDate}
            min={today}
            onChange={(e) => onStartDateChange(e.target.value)}
          />
          {errors?.startDate && (
            <p className="text-xs text-destructive">{errors.startDate.message}</p>
          )}
        </div>
        <div className="space-y-2">
          <Label htmlFor="leave-end">End Date *</Label>
          <Input
            id="leave-end"
            type="date"
            value={endDate}
            min={startDate || today}
            onChange={(e) => onEndDateChange(e.target.value)}
          />
          {errors?.endDate && <p className="text-xs text-destructive">{errors.endDate.message}</p>}
        </div>
      </div>

      {onHalfDayChange && (
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Checkbox
              id="halfDay"
              checked={halfDay}
              onCheckedChange={(checked) => onHalfDayChange(!!checked)}
            />
            <Label htmlFor="halfDay" className="text-sm font-normal">
              Half Day
            </Label>
          </div>
          {halfDay && onHalfDayPeriodChange && (
            <Select value={halfDayPeriod ?? ''} onValueChange={onHalfDayPeriodChange}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Select period" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="morning">Morning</SelectItem>
                <SelectItem value="afternoon">Afternoon</SelectItem>
              </SelectContent>
            </Select>
          )}
        </div>
      )}

      <div className="flex items-center gap-3">
        {workingDays > 0 && (
          <Badge variant="secondary">
            {workingDays} working day{workingDays !== 1 ? 's' : ''}
          </Badge>
        )}
        {leaveBalance && (
          <Badge variant="outline">
            Balance: {leaveBalance.remaining}/{leaveBalance.totalEntitlement} days
          </Badge>
        )}
      </div>

      {validationError && <p className="text-xs text-destructive">{validationError}</p>}
    </div>
  );
}
