'use client';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { LeaveType } from '@/types/hr';

interface LeaveTypeSelectProps {
  value: string;
  onChange: (value: string) => void;
}

const leaveTypeLabels: Record<string, string> = {
  [LeaveType.ANNUAL]: 'Annual Leave',
  [LeaveType.SICK]: 'Sick Leave',
  [LeaveType.UNPAID]: 'Unpaid Leave',
  [LeaveType.MATERNITY]: 'Maternity Leave',
  [LeaveType.PATERNITY]: 'Paternity Leave',
  [LeaveType.BEREAVEMENT]: 'Bereavement Leave',
  [LeaveType.STUDY]: 'Study Leave',
};

export function LeaveTypeSelect({ value, onChange }: LeaveTypeSelectProps) {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger>
        <SelectValue placeholder="Select leave type" />
      </SelectTrigger>
      <SelectContent>
        {Object.entries(leaveTypeLabels).map(([key, label]) => (
          <SelectItem key={key} value={key}>
            {label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
