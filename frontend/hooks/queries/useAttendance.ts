/**
 * useAttendance — fetch paginated attendance records
 */

import { useQuery } from '@tanstack/react-query';
import { hrKeys } from '@/lib/queryKeys';
import { attendanceService } from '@/services/api';

interface AttendanceFilters {
  employeeId?: string;
  departmentId?: string;
  status?: 'all' | 'present' | 'absent' | 'late' | 'on_leave';
  startDate: string;
  endDate: string;
  sortBy?: 'date' | 'employee';
  sortOrder?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

export type { AttendanceFilters };

export function useAttendance(filters: AttendanceFilters) {
  return useQuery({
    queryKey: hrKeys.attendance(),
    queryFn: () => attendanceService.getAttendance(filters),
    staleTime: 30 * 1000,
    placeholderData: (prev) => prev,
    refetchOnWindowFocus: true,
  });
}
