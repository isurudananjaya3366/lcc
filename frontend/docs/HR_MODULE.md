# HR & Payroll Module Documentation

## Overview

The HR & Payroll module provides comprehensive human resource management including employee records, attendance tracking, leave management, payroll processing, and organizational structure management. Built for Sri Lankan businesses with EPF/ETF compliance and LKR currency support.

## Module Structure

```
components/modules/hr/
├── Employees/
│   ├── EmployeesList.tsx          # Main employee listing (cards/table)
│   ├── EmployeesHeader.tsx        # Title + Add Employee button
│   ├── EmployeeSummaryCards.tsx    # Total/Active/Departments overview
│   ├── EmployeeFilters.tsx        # Search, department, status filters
│   ├── EmployeeCard.tsx           # Individual employee card
│   ├── EmployeeCardsGrid.tsx      # Responsive cards grid layout
│   ├── EmployeesTable.tsx         # Tabular employee listing
│   ├── EmployeeAvatar.tsx         # Avatar with initials
│   ├── ViewToggle.tsx             # Cards/Table view switcher
│   ├── StatusFilter.tsx           # Employee status filter
│   ├── DepartmentFilter.tsx       # Department filter
│   ├── EmployeeProfile/
│   │   ├── EmployeeDetails.tsx    # Profile container
│   │   ├── EmployeeProfileHeader.tsx
│   │   ├── EmployeeTabs.tsx       # Personal/Employment tabs
│   │   ├── PersonalInfoTab.tsx
│   │   └── EmploymentInfoTab.tsx
│   ├── EmployeeForm/
│   │   ├── EmployeeForm.tsx       # Add employee form container
│   │   ├── PersonalInfoSection.tsx # NIC, DOB, gender
│   │   ├── ContactInfoSection.tsx  # Phone, email, address
│   │   ├── EmploymentInfoSection.tsx # Dept, position, salary
│   │   └── DocumentUploadSection.tsx # File uploads
│   └── OrgChart/
│       ├── OrgChartPage.tsx       # Organizational chart
│       └── OrgChartNode.tsx       # Tree node component
├── Attendance/
│   ├── AttendanceDashboard.tsx    # Main attendance page
│   ├── AttendanceHeader.tsx       # Date navigation + actions
│   ├── TodaySummaryCards.tsx      # Present/Absent/Late counts
│   ├── AttendanceCalendar.tsx     # Monthly calendar view
│   ├── CalendarDayCell.tsx        # Calendar cell with status
│   ├── AttendanceLegend.tsx       # Status color legend
│   ├── AttendanceRow.tsx          # Employee attendance row
│   ├── DailyAttendanceList.tsx    # Daily record list
│   ├── ManualEntryModal.tsx       # Manual attendance entry
│   ├── ClockInOutButton.tsx       # Check-in/out with timer
│   ├── AttendanceFilters.tsx      # Search + status filter
│   └── Reports/
│       ├── AttendanceReport.tsx   # Report page container
│       ├── DateRangeSelector.tsx
│       ├── AttendanceReportTable.tsx
│       └── ExportAttendance.tsx
├── Leave/
│   ├── LeaveDashboard.tsx         # Main leave page
│   ├── LeaveHeader.tsx            # Title + Request Leave
│   ├── LeaveBalanceCards.tsx       # Leave balance overview
│   ├── LeaveBalanceCard.tsx       # Individual balance card
│   ├── LeaveRequestsTable.tsx     # Requests table + actions
│   ├── LeaveStatusBadge.tsx       # Status badge component
│   ├── LeaveTypeSelect.tsx        # Leave type dropdown
│   ├── LeaveCalendar.tsx          # Team leave calendar
│   ├── LeaveRequestForm.tsx       # Submit leave request
│   └── ApprovalModal.tsx          # Approve/reject dialog
├── Payroll/
│   ├── PayrollDashboard.tsx       # Main payroll page
│   ├── PayrollHeader.tsx          # Title + Run Payroll
│   ├── PayrollSummaryCards.tsx    # Total/Pending/Processed
│   ├── PayrollPeriodsTable.tsx   # Payroll runs table
│   ├── PeriodStatusBadge.tsx     # Run status badge
│   ├── PayrollRun/
│   │   ├── PayrollRunPage.tsx     # 4-step wizard
│   │   ├── PeriodSelectionStep.tsx
│   │   ├── EmployeeSelectionStep.tsx
│   │   ├── ReviewCalculationsStep.tsx # EPF/ETF/PAYE calc
│   │   └── ConfirmProcessingStep.tsx
│   └── Payslip/
│       ├── PayslipDetails.tsx     # Payslip detail page
│       ├── PayslipHeader.tsx
│       ├── PayslipEarnings.tsx
│       ├── PayslipDeductions.tsx
│       └── PayslipPDF.tsx         # PDF download button
└── Settings/
    ├── DepartmentManagement.tsx   # CRUD department table
    ├── DepartmentModal.tsx        # Create/edit department
    ├── PositionManagement.tsx     # CRUD position table
    └── PositionModal.tsx          # Create/edit position
```

## Hooks

| Hook | File | Purpose |
|------|------|---------|
| `useEmployees` | `hooks/hr/useEmployees.ts` | Employee CRUD, departments, positions |
| `useAttendance` | `hooks/hr/useAttendance.ts` | Attendance records, check-in/out |
| `useLeave` | `hooks/hr/useLeave.ts` | Leave requests, balances, approvals |
| `usePayroll` | `hooks/hr/usePayroll.ts` | Payroll runs, payslips, processing |

## Services

| Service | File | Endpoints |
|---------|------|-----------|
| `employeeService` | `services/api/employeeService.ts` | `/api/v1/employees/`, `/api/v1/departments/`, `/api/v1/positions/` |
| `attendanceService` | `services/api/attendanceService.ts` | `/api/v1/attendance/` |
| `leaveService` | `services/api/leaveService.ts` | `/api/v1/leave/` |
| `payrollService` | `services/api/payrollService.ts` | `/api/v1/payroll/` |

## Routes

| Route | Page | Component |
|-------|------|-----------|
| `/employees` | Employee listing | `EmployeesList` |
| `/employees/new` | Add employee | `EmployeeForm` |
| `/employees/[id]` | Employee profile | `EmployeeDetails` |
| `/employees/org-chart` | Org chart | `OrgChartPage` |
| `/attendance` | Attendance dashboard | `AttendanceDashboard` |
| `/attendance/reports` | Attendance reports | `AttendanceReport` |
| `/leave` | Leave dashboard | `LeaveDashboard` |
| `/leave/request` | Leave request form | `LeaveRequestForm` |
| `/payroll` | Payroll dashboard | `PayrollDashboard` |
| `/payroll/run` | Payroll wizard | `PayrollRunPage` |
| `/payroll/[id]` | Payslip details | `PayslipDetails` |

## Sri Lanka Compliance

- **EPF (Employee):** 8% of basic salary
- **EPF (Employer):** 12% of basic salary
- **ETF:** 3% of basic salary
- **PAYE Tax:** Slab-based calculation on annual income
- **NIC Validation:** Old format (9 digits + V/X) and new format (12 digits)
- **Phone Format:** Sri Lankan mobile numbers (0xx format, 10 digits)
- **Currency:** LKR (₨) with `en-LK` locale formatting

## Types

All HR types are defined in `types/hr.ts`:
- `Employee`, `Department`, `Position`
- `EmploymentType`, `EmployeeStatus`
- `LeaveType`, `LeaveStatus`, `LeaveBalance`, `LeaveRequest`
- `AttendanceStatus`, `Attendance`
- `Payroll`, `PayrollItem`
