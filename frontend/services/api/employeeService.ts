/**
 * Employee Service
 *
 * Type-safe CRUD operations for employees, departments, and positions.
 * Includes termination, reactivation, and org-structure queries.
 */

import { apiClient } from './apiClient';
import type { APIResponse, PaginatedResponse } from '@/types/api';
import type {
  Employee,
  EmployeeCreateRequest,
  EmployeeUpdateRequest,
  EmployeeSearchParams,
  Department,
  Position,
} from '@/types/hr';

const EMPLOYEE_ENDPOINT = '/api/v1/employees';
const DEPARTMENT_ENDPOINT = '/api/v1/departments';
const POSITION_ENDPOINT = '/api/v1/positions';

// ── Employee CRUD ──────────────────────────────────────────────

async function getEmployees(
  params?: EmployeeSearchParams
): Promise<PaginatedResponse<Employee>> {
  const { data } = await apiClient.get(`${EMPLOYEE_ENDPOINT}/`, { params });
  return data;
}

async function getEmployeeById(id: string): Promise<APIResponse<Employee>> {
  const { data } = await apiClient.get(`${EMPLOYEE_ENDPOINT}/${id}/`);
  return data;
}

async function getEmployeeByNumber(
  employeeNumber: string
): Promise<APIResponse<Employee>> {
  const { data } = await apiClient.get(
    `${EMPLOYEE_ENDPOINT}/by-number/${employeeNumber}/`
  );
  return data;
}

async function createEmployee(
  employeeData: EmployeeCreateRequest
): Promise<APIResponse<Employee>> {
  const { data } = await apiClient.post(`${EMPLOYEE_ENDPOINT}/`, employeeData);
  return data;
}

async function updateEmployee(
  id: string,
  employeeData: EmployeeUpdateRequest
): Promise<APIResponse<Employee>> {
  const { data } = await apiClient.patch(
    `${EMPLOYEE_ENDPOINT}/${id}/`,
    employeeData
  );
  return data;
}

async function deleteEmployee(id: string): Promise<APIResponse<void>> {
  const { data } = await apiClient.delete(`${EMPLOYEE_ENDPOINT}/${id}/`);
  return data;
}

async function terminateEmployee(
  id: string,
  terminationData: { date: string; reason: string }
): Promise<APIResponse<Employee>> {
  const { data } = await apiClient.post(
    `${EMPLOYEE_ENDPOINT}/${id}/terminate/`,
    terminationData
  );
  return data;
}

async function reactivateEmployee(
  id: string
): Promise<APIResponse<Employee>> {
  const { data } = await apiClient.post(
    `${EMPLOYEE_ENDPOINT}/${id}/reactivate/`
  );
  return data;
}

async function getEmployeesByDepartment(
  departmentId: string
): Promise<PaginatedResponse<Employee>> {
  const { data } = await apiClient.get(`${EMPLOYEE_ENDPOINT}/`, {
    params: { departmentId },
  });
  return data;
}

async function getEmployeesByManager(
  managerId: string
): Promise<PaginatedResponse<Employee>> {
  const { data } = await apiClient.get(`${EMPLOYEE_ENDPOINT}/`, {
    params: { managerId },
  });
  return data;
}

// ── Departments ────────────────────────────────────────────────

async function getDepartments(): Promise<APIResponse<Department[]>> {
  const { data } = await apiClient.get(`${DEPARTMENT_ENDPOINT}/`);
  return data;
}

async function getDepartmentById(
  id: string
): Promise<APIResponse<Department>> {
  const { data } = await apiClient.get(`${DEPARTMENT_ENDPOINT}/${id}/`);
  return data;
}

async function createDepartment(
  departmentData: Omit<Department, 'id'>
): Promise<APIResponse<Department>> {
  const { data } = await apiClient.post(`${DEPARTMENT_ENDPOINT}/`, departmentData);
  return data;
}

async function updateDepartment(
  id: string,
  departmentData: Partial<Department>
): Promise<APIResponse<Department>> {
  const { data } = await apiClient.patch(
    `${DEPARTMENT_ENDPOINT}/${id}/`,
    departmentData
  );
  return data;
}

async function deleteDepartment(id: string): Promise<APIResponse<void>> {
  const { data } = await apiClient.delete(`${DEPARTMENT_ENDPOINT}/${id}/`);
  return data;
}

// ── Positions ──────────────────────────────────────────────────

async function getPositions(): Promise<APIResponse<Position[]>> {
  const { data } = await apiClient.get(`${POSITION_ENDPOINT}/`);
  return data;
}

async function getPositionById(id: string): Promise<APIResponse<Position>> {
  const { data } = await apiClient.get(`${POSITION_ENDPOINT}/${id}/`);
  return data;
}

async function createPosition(
  positionData: Omit<Position, 'id'>
): Promise<APIResponse<Position>> {
  const { data } = await apiClient.post(`${POSITION_ENDPOINT}/`, positionData);
  return data;
}

async function updatePosition(
  id: string,
  positionData: Partial<Position>
): Promise<APIResponse<Position>> {
  const { data } = await apiClient.patch(
    `${POSITION_ENDPOINT}/${id}/`,
    positionData
  );
  return data;
}

async function deletePosition(id: string): Promise<APIResponse<void>> {
  const { data } = await apiClient.delete(`${POSITION_ENDPOINT}/${id}/`);
  return data;
}

const employeeService = {
  getEmployees,
  getEmployeeById,
  getEmployeeByNumber,
  createEmployee,
  updateEmployee,
  deleteEmployee,
  terminateEmployee,
  reactivateEmployee,
  getEmployeesByDepartment,
  getEmployeesByManager,
  getDepartments,
  getDepartmentById,
  createDepartment,
  updateDepartment,
  deleteDepartment,
  getPositions,
  getPositionById,
  createPosition,
  updatePosition,
  deletePosition,
};

export default employeeService;
