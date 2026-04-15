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
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useMarkAttendance } from '@/hooks/hr/useAttendance';
import { AttendanceStatus } from '@/types/hr';

interface ManualEntryModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultDate?: string;
}

export function ManualEntryModal({ open, onOpenChange, defaultDate }: ManualEntryModalProps) {
  const [employeeId, setEmployeeId] = useState('');
  const [date, setDate] = useState(defaultDate ?? new Date().toISOString().slice(0, 10));
  const [status, setStatus] = useState<AttendanceStatus>(AttendanceStatus.PRESENT);
  const [notes, setNotes] = useState('');

  const markMutation = useMarkAttendance();

  const handleSubmit = () => {
    if (!employeeId || !date) return;
    markMutation.mutate(
      { employeeId, date, status, notes: notes || undefined },
      {
        onSuccess: () => {
          onOpenChange(false);
          setEmployeeId('');
          setNotes('');
        },
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Manual Attendance Entry</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="employeeId">Employee ID</Label>
            <Input
              id="employeeId"
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              placeholder="Enter employee ID"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="date">Date</Label>
            <Input id="date" type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label>Status</Label>
            <Select value={status} onValueChange={(v) => setStatus(v as AttendanceStatus)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={AttendanceStatus.PRESENT}>Present</SelectItem>
                <SelectItem value={AttendanceStatus.ABSENT}>Absent</SelectItem>
                <SelectItem value={AttendanceStatus.LATE}>Late</SelectItem>
                <SelectItem value={AttendanceStatus.HALF_DAY}>Half Day</SelectItem>
                <SelectItem value={AttendanceStatus.ON_LEAVE}>On Leave</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Optional notes"
              maxLength={500}
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={!employeeId || !date || markMutation.isPending}>
            {markMutation.isPending ? 'Saving...' : 'Save Entry'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
