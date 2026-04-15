'use client';

import { useMemo } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface DateRangeSelectorProps {
  startDate: string;
  endDate: string;
  onStartDateChange: (date: string) => void;
  onEndDateChange: (date: string) => void;
}

function toISO(d: Date): string {
  return d.toISOString().slice(0, 10);
}

function daysAgo(n: number): string {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return toISO(d);
}

function startOfWeek(): string {
  const d = new Date();
  d.setDate(d.getDate() - d.getDay());
  return toISO(d);
}

function startOfMonth(): string {
  const d = new Date();
  return toISO(new Date(d.getFullYear(), d.getMonth(), 1));
}

function startOfQuarter(): string {
  const d = new Date();
  const q = Math.floor(d.getMonth() / 3) * 3;
  return toISO(new Date(d.getFullYear(), q, 1));
}

function startOfYear(): string {
  return toISO(new Date(new Date().getFullYear(), 0, 1));
}

const presets = [
  { label: 'Today', start: () => toISO(new Date()), end: () => toISO(new Date()) },
  { label: 'This Week', start: startOfWeek, end: () => toISO(new Date()) },
  { label: 'This Month', start: startOfMonth, end: () => toISO(new Date()) },
  { label: 'This Quarter', start: startOfQuarter, end: () => toISO(new Date()) },
  { label: 'This Year', start: startOfYear, end: () => toISO(new Date()) },
  { label: 'Last 7 Days', start: () => daysAgo(7), end: () => toISO(new Date()) },
  { label: 'Last 30 Days', start: () => daysAgo(30), end: () => toISO(new Date()) },
  { label: 'Last 90 Days', start: () => daysAgo(90), end: () => toISO(new Date()) },
];

export function DateRangeSelector({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
}: DateRangeSelectorProps) {
  const today = toISO(new Date());

  const validationError = useMemo(() => {
    if (!startDate || !endDate) return null;
    if (startDate > endDate) return 'Start date must be before end date';
    if (endDate > today) return 'End date cannot be in the future';
    const diffMs = new Date(endDate).getTime() - new Date(startDate).getTime();
    const diffDays = diffMs / (1000 * 60 * 60 * 24);
    if (diffDays > 365) return 'Maximum range is 365 days';
    return null;
  }, [startDate, endDate, today]);

  const dayCount = useMemo(() => {
    if (!startDate || !endDate || startDate > endDate) return 0;
    const diffMs = new Date(endDate).getTime() - new Date(startDate).getTime();
    return Math.round(diffMs / (1000 * 60 * 60 * 24)) + 1;
  }, [startDate, endDate]);

  const applyPreset = (preset: (typeof presets)[number]) => {
    onStartDateChange(preset.start());
    onEndDateChange(preset.end());
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {presets.map((p) => (
          <Button
            key={p.label}
            variant="outline"
            size="sm"
            className="text-xs"
            onClick={() => applyPreset(p)}
          >
            {p.label}
          </Button>
        ))}
      </div>

      <div className="flex items-end gap-4">
        <div className="space-y-2">
          <Label htmlFor="startDate">From</Label>
          <Input
            id="startDate"
            type="date"
            value={startDate}
            max={today}
            onChange={(e) => onStartDateChange(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="endDate">To</Label>
          <Input
            id="endDate"
            type="date"
            value={endDate}
            max={today}
            onChange={(e) => onEndDateChange(e.target.value)}
          />
        </div>
        {dayCount > 0 && !validationError && (
          <Badge variant="secondary" className="mb-2">
            {dayCount} day{dayCount > 1 ? 's' : ''} selected
          </Badge>
        )}
      </div>

      {validationError && <p className="text-xs text-destructive">{validationError}</p>}
    </div>
  );
}
