'use client';

import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight, Plus } from 'lucide-react';

interface AttendanceHeaderProps {
  selectedDate: Date;
  onDateChange: (date: Date) => void;
  onManualEntry?: () => void;
}

export function AttendanceHeader({
  selectedDate,
  onDateChange,
  onManualEntry,
}: AttendanceHeaderProps) {
  const goToPrev = () => {
    const d = new Date(selectedDate);
    d.setDate(d.getDate() - 1);
    onDateChange(d);
  };

  const goToNext = () => {
    const d = new Date(selectedDate);
    d.setDate(d.getDate() + 1);
    onDateChange(d);
  };

  const goToToday = () => onDateChange(new Date());

  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Attendance</h1>
        <p className="text-muted-foreground">Track employee attendance and work hours</p>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1">
          <Button variant="outline" size="icon" onClick={goToPrev}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={goToToday}>
            Today
          </Button>
          <span className="px-3 text-sm font-medium">
            {selectedDate.toLocaleDateString('en-LK', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </span>
          <Button variant="outline" size="icon" onClick={goToNext}>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
        {onManualEntry && (
          <Button onClick={onManualEntry}>
            <Plus className="mr-2 h-4 w-4" />
            Manual Entry
          </Button>
        )}
      </div>
    </div>
  );
}
