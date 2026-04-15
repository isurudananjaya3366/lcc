'use client';

import { useState, useMemo } from 'react';
import { useAttendance } from '@/hooks/hr/useAttendance';
import { AttendanceHeader } from './AttendanceHeader';
import { TodaySummaryCards } from './TodaySummaryCards';
import { AttendanceCalendar } from './AttendanceCalendar';
import { DailyAttendanceList } from './DailyAttendanceList';
import { AttendanceFilters, type AttendanceFilterState } from './AttendanceFilters';
import { ClockInOutButton } from './ClockInOutButton';
import { ManualEntryModal } from './ManualEntryModal';

export function AttendanceDashboard() {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [calMonth, setCalMonth] = useState(new Date().getMonth());
  const [calYear, setCalYear] = useState(new Date().getFullYear());
  const [showManualEntry, setShowManualEntry] = useState(false);
  const [filters, setFilters] = useState<AttendanceFilterState>({
    search: '',
    status: 'all',
    department: 'all',
    dateRange: 'all',
    attendanceType: 'all',
  });

  const startOfMonth = new Date(calYear, calMonth, 1).toISOString().slice(0, 10);
  const endOfMonth = new Date(calYear, calMonth + 1, 0).toISOString().slice(0, 10);

  const { data } = useAttendance({
    startDate: startOfMonth,
    endDate: endOfMonth,
    employeeId: filters.search || undefined,
    status: filters.status !== 'all' ? filters.status : undefined,
  });

  const records = data?.data ?? [];

  const todayStr = selectedDate.toISOString().slice(0, 10);
  const todayRecords = useMemo(
    () => records.filter((r) => r.date.startsWith(todayStr)),
    [records, todayStr]
  );

  const presentCount = todayRecords.filter((r) => r.status === 'PRESENT').length;
  const absentCount = todayRecords.filter((r) => r.status === 'ABSENT').length;
  const lateCount = todayRecords.filter((r) => r.status === 'LATE').length;

  const handleDayClick = (date: Date) => setSelectedDate(date);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <AttendanceHeader
          selectedDate={selectedDate}
          onDateChange={setSelectedDate}
          onManualEntry={() => setShowManualEntry(true)}
        />
        <ClockInOutButton employeeId="current" />
      </div>

      <TodaySummaryCards
        presentCount={presentCount}
        absentCount={absentCount}
        lateCount={lateCount}
        totalEmployees={todayRecords.length || 1}
      />

      <AttendanceFilters filters={filters} onFiltersChange={setFilters} />

      <div className="grid gap-6 lg:grid-cols-5">
        <div className="lg:col-span-3">
          <AttendanceCalendar
            month={calMonth}
            year={calYear}
            records={records}
            onMonthChange={(m, y) => {
              setCalMonth(m);
              setCalYear(y);
            }}
            onDayClick={handleDayClick}
          />
        </div>
        <div className="lg:col-span-2">
          <DailyAttendanceList records={todayRecords} selectedDate={selectedDate} />
        </div>
      </div>

      <ManualEntryModal
        open={showManualEntry}
        onOpenChange={setShowManualEntry}
        defaultDate={todayStr}
      />
    </div>
  );
}
