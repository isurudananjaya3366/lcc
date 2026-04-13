/**
 * HR Types
 *
 * Comprehensive TypeScript types for human resources management
 * including employees, departments, attendance, leave, and payroll.
 */

// ── Enums ──────────────────────────────────────────────────────

export enum EmploymentType {
  FULL_TIME = 'FULL_TIME',
  PART_TIME = 'PART_TIME',
  CONTRACT = 'CONTRACT',
  TEMPORARY = 'TEMPORARY',
  INTERN = 'INTERN',
}

export enum EmployeeStatus {
  ACTIVE = 'ACTIVE',
  ON_LEAVE = 'ON_LEAVE',
  SUSPENDED = 'SUSPENDED',
  TERMINATED = 'TERMINATED',
  RETIRED = 'RETIRED',
}

export enum LeaveType {
  ANNUAL = 'ANNUAL',
  SICK = 'SICK',
  UNPAID = 'UNPAID',
  MATERNITY = 'MATERNITY',
  PATERNITY = 'PATERNITY',
  BEREAVEMENT = 'BEREAVEMENT',
  STUDY = 'STUDY',
}

export enum LeaveStatus {
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  CANCELLED = 'CANCELLED',
}

export enum AttendanceStatus {
  PRESENT = 'PRESENT',
  ABSENT = 'ABSENT',
  LATE = 'LATE',
  HALF_DAY = 'HALF_DAY',
  ON_LEAVE = 'ON_LEAVE',
}

// ── Supporting Interfaces ──────────────────────────────────────

export interface Department {
  id: string;
  name: string;
  code: string;
  description?: string;
  managerId?: string;
  parentDepartmentId?: string;
  employeeCount: number;
  isActive: boolean;
}

export interface Position {
  id: string;
  title: string;
  code: string;
  description?: string;
  departmentId: string;
  level?: string;
  category?: string;
  isActive: boolean;
}

export interface LeaveBalance {
  id: string;
  employeeId: string;
  leaveType: LeaveType;
  year: number;
  totalEntitlement: number;
  used: number;
  remaining: number;
  pending: number;
}

export interface LeaveRequest {
  id: string;
  employeeId: string;
  leaveType: LeaveType;
  status: LeaveStatus;
  startDate: string;
  endDate: string;
  days: number;
  reason?: string;
  approvedBy?: string;
  approvalDate?: string;
  rejectionReason?: string;
  createdAt: string;
}

export interface Attendance {
  id: string;
  employeeId: string;
  date: string;
  status: AttendanceStatus;
  checkInTime?: string;
  checkOutTime?: string;
  workHours?: number;
  isLate: boolean;
  lateMinutes?: number;
  notes?: string;
  recordedBy?: string;
}

export interface Payroll {
  id: string;
  payrollNumber: string;
  period: string;
  status: 'DRAFT' | 'PROCESSING' | 'PROCESSED' | 'PAID';
  processedDate?: string;
  paymentDate?: string;
  employeeCount: number;
  totalGross: number;
  totalDeductions: number;
  totalNet: number;
  processedBy?: string;
}

export interface PayrollItem {
  id: string;
  payrollId: string;
  employeeId: string;
  basicSalary: number;
  allowances: { name: string; amount: number }[];
  deductions: { name: string; amount: number }[];
  grossPay: number;
  netPay: number;
  taxAmount: number;
  workingDays: number;
  paidDays: number;
  absences: number;
}

// ── Main Entity ────────────────────────────────────────────────

export interface Employee {
  id: string;
  tenantId: string;
  employeeNumber: string;
  userId?: string;
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  dateOfBirth?: string;
  gender?: string;
  nationality?: string;
  employmentType: EmploymentType;
  status: EmployeeStatus;
  departmentId: string;
  positionId: string;
  hireDate: string;
  terminationDate?: string;
  probationEndDate?: string;
  managerId?: string;
  workLocation?: string;
  emergencyContact?: {
    name: string;
    relationship: string;
    phone: string;
  };
  bankAccount?: {
    bankName: string;
    accountNumber: string;
  };
  taxId?: string;
  socialSecurityNumber?: string;
  salary?: number;
  payrollSchedule?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

// ── API Request/Response Interfaces ────────────────────────────

export interface EmployeeCreateRequest {
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  dateOfBirth?: string;
  gender?: string;
  nationality?: string;
  employmentType: EmploymentType;
  departmentId: string;
  positionId: string;
  hireDate: string;
  probationEndDate?: string;
  managerId?: string;
  workLocation?: string;
  emergencyContact?: {
    name: string;
    relationship: string;
    phone: string;
  };
  bankAccount?: {
    bankName: string;
    accountNumber: string;
  };
  taxId?: string;
  salary?: number;
}

export interface EmployeeUpdateRequest {
  firstName?: string;
  lastName?: string;
  email?: string;
  phone?: string;
  employmentType?: EmploymentType;
  status?: EmployeeStatus;
  departmentId?: string;
  positionId?: string;
  managerId?: string;
  workLocation?: string;
  emergencyContact?: {
    name: string;
    relationship: string;
    phone: string;
  };
  bankAccount?: {
    bankName: string;
    accountNumber: string;
  };
  salary?: number;
}

export interface EmployeeSearchParams {
  query?: string;
  departmentId?: string;
  positionId?: string;
  status?: EmployeeStatus;
  employmentType?: EmploymentType;
  managerId?: string;
  sort?: string;
  page?: number;
  pageSize?: number;
}
