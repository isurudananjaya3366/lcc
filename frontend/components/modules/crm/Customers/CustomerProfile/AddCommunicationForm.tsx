'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
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
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { customerKeys } from '@/lib/queryKeys';
import { apiClient } from '@/services/api/apiClient';

interface AddCommunicationFormProps {
  customerId: string;
  isOpen: boolean;
  onSuccess?: () => void;
  onClose: () => void;
}

const CUSTOMER_ENDPOINT = '/api/v1/customers';

export function AddCommunicationForm({
  customerId,
  isOpen,
  onSuccess,
  onClose,
}: AddCommunicationFormProps) {
  const queryClient = useQueryClient();
  const [type, setType] = useState('');
  const [subject, setSubject] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [time, setTime] = useState('');
  const [notes, setNotes] = useState('');

  const mutation = useMutation({
    mutationFn: async (data: {
      type: string;
      subject: string;
      date: string;
      time?: string;
      notes?: string;
    }) => {
      const response = await apiClient.post(
        `${CUSTOMER_ENDPOINT}/${customerId}/communications/`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: customerKeys.detail(customerId) });
      resetForm();
      onSuccess?.();
      onClose();
    },
  });

  function resetForm() {
    setType('');
    setSubject('');
    setDate(new Date().toISOString().split('T')[0]);
    setTime('');
    setNotes('');
  }

  const isValid = type && subject.trim().length > 0 && subject.length <= 200 && date;

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add Communication Entry</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="comm-type">Type *</Label>
            <Select value={type} onValueChange={setType}>
              <SelectTrigger id="comm-type">
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="phone">Phone Call</SelectItem>
                <SelectItem value="email">Email</SelectItem>
                <SelectItem value="meeting">Meeting</SelectItem>
                <SelectItem value="note">Note</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="comm-subject">Subject *</Label>
            <Input
              id="comm-subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              maxLength={200}
              placeholder="Brief subject description"
            />
            <p className="text-xs text-muted-foreground">{subject.length}/200</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="comm-date">Date *</Label>
              <Input
                id="comm-date"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="comm-time">Time</Label>
              <Input
                id="comm-time"
                type="time"
                value={time}
                onChange={(e) => setTime(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="comm-notes">Notes</Label>
            <Textarea
              id="comm-notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              maxLength={1000}
              rows={4}
              placeholder="Additional notes..."
            />
            <p className="text-xs text-muted-foreground">{notes.length}/1000</p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={() =>
              mutation.mutate({
                type,
                subject,
                date: date || new Date().toISOString().split('T')[0]!,
                time: time || undefined,
                notes: notes || undefined,
              })
            }
            disabled={!isValid || mutation.isPending}
          >
            {mutation.isPending ? 'Saving...' : 'Save Entry'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
