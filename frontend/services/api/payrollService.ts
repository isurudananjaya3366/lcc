/**
 * Payroll Service
 *
 * Type-safe operations for payroll runs, processing, payroll items,
 * employee payslips, and PDF downloads.
 */

import { apiClient } from './apiClient';
import type { APIResponse, PaginatedResponse } from '@/types/api';
import type { Payroll, PayrollItem } from '@/types/hr';

const PAYROLL_ENDPOINT = '/api/v1/payroll';

async function getPayrollRuns(params?: {
  month?: number;
  year?: number;
  status?: string;
}): Promise<PaginatedResponse<Payroll>> {
  const { data } = await apiClient.get(`${PAYROLL_ENDPOINT}/`, { params });
  return data;
}

async function getPayrollById(id: string): Promise<APIResponse<Payroll>> {
  const { data } = await apiClient.get(`${PAYROLL_ENDPOINT}/${id}/`);
  return data;
}

async function createPayrollRun(payrollData: {
  month: number;
  year: number;
  description?: string;
}): Promise<APIResponse<Payroll>> {
  const { data } = await apiClient.post(`${PAYROLL_ENDPOINT}/`, payrollData);
  return data;
}

async function processPayroll(id: string): Promise<APIResponse<Payroll>> {
  const { data } = await apiClient.post(`${PAYROLL_ENDPOINT}/${id}/process/`);
  return data;
}

async function approvePayroll(id: string): Promise<APIResponse<Payroll>> {
  const { data } = await apiClient.post(`${PAYROLL_ENDPOINT}/${id}/approve/`);
  return data;
}

async function getPayrollItems(
  payrollId: string
): Promise<APIResponse<PayrollItem[]>> {
  const { data } = await apiClient.get(`${PAYROLL_ENDPOINT}/${payrollId}/items/`);
  return data;
}

async function getEmployeePayslips(
  employeeId: string,
  params?: { year?: number }
): Promise<PaginatedResponse<PayrollItem>> {
  const { data } = await apiClient.get(
    `${PAYROLL_ENDPOINT}/payslips/${employeeId}/`,
    { params }
  );
  return data;
}

async function downloadPayslipPdf(
  payrollId: string,
  employeeId: string
): Promise<Blob> {
  const { data } = await apiClient.get(
    `${PAYROLL_ENDPOINT}/${payrollId}/payslips/${employeeId}/pdf/`,
    { responseType: 'blob' }
  );
  return data;
}

const payrollService = {
  getPayrollRuns,
  getPayrollById,
  createPayrollRun,
  processPayroll,
  approvePayroll,
  getPayrollItems,
  getEmployeePayslips,
  downloadPayslipPdf,
};

export default payrollService;
