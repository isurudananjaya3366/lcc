/**
 * Attendance Service
 *
 * Type-safe operations for employee time tracking — check-in/out,
 * attendance records, summaries, and department-level queries.
 */

import { apiClient } from './apiClient';
import type { APIResponse, PaginatedResponse } from '@/types/api';
import type { Attendance, AttendanceStatus } from '@/types/hr';

const ATTENDANCE_ENDPOINT = '/api/v1/attendance';

async function checkIn(
  employeeId: string,
  location?: string
): Promise<APIResponse<Attendance>> {
  const { data } = await apiClient.post(`${ATTENDANCE_ENDPOINT}/check-in/`, {
    employeeId,
    location,
  });
  return data;
}

async function checkOut(
  attendanceId: string,
  location?: string
): Promise<APIResponse<Attendance>> {
  const { data } = await apiClient.post(
    `${ATTENDANCE_ENDPOINT}/${attendanceId}/check-out/`,
    { location }
  );
  return data;
}

async function markAttendance(
  employeeId: string,
  date: string,
  status: AttendanceStatus,
  notes?: string
): Promise<APIResponse<Attendance>> {
  const { data } = await apiClient.post(`${ATTENDANCE_ENDPOINT}/mark/`, {
    employeeId,
    date,
    status,
    notes,
  });
  return data;
}

async function getAttendance(params?: {
  employeeId?: string;
  startDate?: string;
  endDate?: string;
  status?: AttendanceStatus;
}): Promise<PaginatedResponse<Attendance>> {
  const { data } = await apiClient.get(`${ATTENDANCE_ENDPOINT}/`, { params });
  return data;
}

async function getAttendanceById(
  id: string
): Promise<APIResponse<Attendance>> {
  const { data } = await apiClient.get(`${ATTENDANCE_ENDPOINT}/${id}/`);
  return data;
}

async function getAttendanceSummary(params: {
  employeeId: string;
  month: number;
  year: number;
}): Promise<
  APIResponse<{
    totalDays: number;
    present: number;
    absent: number;
    late: number;
    halfDay: number;
    leave: number;
    totalHoursWorked: number;
  }>
> {
  const { data } = await apiClient.get(`${ATTENDANCE_ENDPOINT}/summary/`, {
    params,
  });
  return data;
}

async function getDepartmentAttendance(
  departmentId: string,
  date: string
): Promise<APIResponse<Attendance[]>> {
  const { data } = await apiClient.get(`${ATTENDANCE_ENDPOINT}/department/`, {
    params: { departmentId, date },
  });
  return data;
}

async function updateAttendance(
  id: string,
  updates: Partial<Pick<Attendance, 'status' | 'notes'>>
): Promise<APIResponse<Attendance>> {
  const { data } = await apiClient.patch(
    `${ATTENDANCE_ENDPOINT}/${id}/`,
    updates
  );
  return data;
}

const attendanceService = {
  checkIn,
  checkOut,
  markAttendance,
  getAttendance,
  getAttendanceById,
  getAttendanceSummary,
  getDepartmentAttendance,
  updateAttendance,
};

export default attendanceService;
