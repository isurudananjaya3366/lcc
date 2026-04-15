import { apiClient } from './apiClient';
import type { APIResponse, PaginatedResponse } from '@/types/api';
import type { LeaveRequest, LeaveBalance, LeaveStatus } from '@/types/hr';

const LEAVE_ENDPOINT = '/api/v1/leave';

async function getLeaveRequests(params?: {
  employeeId?: string;
  status?: LeaveStatus;
  startDate?: string;
  endDate?: string;
  page?: number;
  pageSize?: number;
}): Promise<PaginatedResponse<LeaveRequest>> {
  const { data } = await apiClient.get(`${LEAVE_ENDPOINT}/requests/`, { params });
  return data;
}

async function getLeaveRequestById(id: string): Promise<APIResponse<LeaveRequest>> {
  const { data } = await apiClient.get(`${LEAVE_ENDPOINT}/requests/${id}/`);
  return data;
}

async function submitLeaveRequest(requestData: {
  leaveType: string;
  startDate: string;
  endDate: string;
  reason?: string;
}): Promise<APIResponse<LeaveRequest>> {
  const { data } = await apiClient.post(`${LEAVE_ENDPOINT}/requests/`, requestData);
  return data;
}

async function approveLeaveRequest(
  id: string,
  comment?: string
): Promise<APIResponse<LeaveRequest>> {
  const { data } = await apiClient.post(`${LEAVE_ENDPOINT}/requests/${id}/approve/`, {
    comment,
  });
  return data;
}

async function rejectLeaveRequest(id: string, reason: string): Promise<APIResponse<LeaveRequest>> {
  const { data } = await apiClient.post(`${LEAVE_ENDPOINT}/requests/${id}/reject/`, {
    reason,
  });
  return data;
}

async function cancelLeaveRequest(id: string): Promise<APIResponse<LeaveRequest>> {
  const { data } = await apiClient.post(`${LEAVE_ENDPOINT}/requests/${id}/cancel/`);
  return data;
}

async function getLeaveBalance(employeeId: string): Promise<APIResponse<LeaveBalance[]>> {
  const { data } = await apiClient.get(`${LEAVE_ENDPOINT}/balance/${employeeId}/`);
  return data;
}

async function getLeaveCalendar(params: {
  startDate: string;
  endDate: string;
  departmentId?: string;
}): Promise<APIResponse<LeaveRequest[]>> {
  const { data } = await apiClient.get(`${LEAVE_ENDPOINT}/calendar/`, { params });
  return data;
}

const leaveService = {
  getLeaveRequests,
  getLeaveRequestById,
  submitLeaveRequest,
  approveLeaveRequest,
  rejectLeaveRequest,
  cancelLeaveRequest,
  getLeaveBalance,
  getLeaveCalendar,
};

async function getLeaveHistory(employeeId: string): Promise<PaginatedResponse<LeaveRequest>> {
  const { data } = await apiClient.get(`${LEAVE_ENDPOINT}/history/${employeeId}/`);
  return data;
}

async function requestMoreInfo(id: string, message: string): Promise<APIResponse<LeaveRequest>> {
  const { data } = await apiClient.post(`${LEAVE_ENDPOINT}/requests/${id}/request-info/`, {
    message,
  });
  return data;
}

async function getTeamCapacity(params: {
  startDate: string;
  endDate: string;
  departmentId?: string;
}): Promise<APIResponse<{ date: string; available: number; total: number }[]>> {
  const { data } = await apiClient.get(`${LEAVE_ENDPOINT}/team-capacity/`, { params });
  return data;
}

async function uploadLeaveAttachment(
  requestId: string,
  file: File
): Promise<APIResponse<{ url: string; filename: string }>> {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await apiClient.post(
    `${LEAVE_ENDPOINT}/requests/${requestId}/upload/`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  );
  return data;
}

const leaveServiceExtended = {
  ...leaveService,
  getLeaveHistory,
  requestMoreInfo,
  getTeamCapacity,
  uploadLeaveAttachment,
};

export default leaveServiceExtended;
