# Leave Management Module

## Overview

The Leave Management module provides a complete employee leave lifecycle for the LankaCommerce Cloud POS system. It supports Sri Lankan labor law compliance, including Annual Leave (14 days), Casual Leave (7 days), Sick Leave (7 days), Maternity Leave (84 days), Paternity Leave, and No-Pay Leave. The module handles leave type configuration, policy management, balance tracking, request workflows, holiday calendars, accrual processing, and reporting.

## Architecture

```
apps/leave/
├── models/
│   ├── __init__.py          # Model exports
│   ├── leave_type.py        # LeaveType configuration (22+ fields)
│   ├── leave_policy.py      # LeavePolicy with scope & entitlement
│   ├── leave_balance.py     # LeaveBalance per employee/type/year
│   ├── leave_request.py     # LeaveRequest with approval workflow
│   └── holiday.py           # Holiday with scope & recurrence
├── services/
│   ├── accrual_service.py   # Annual grant, monthly, pro-rata, carry-forward
│   ├── request_service.py   # Leave request CRUD & lifecycle
│   ├── calendar_service.py  # Working days, team calendar, holidays
│   ├── report_service.py    # Reports & analytics
│   ├── export_service.py    # CSV/Excel export
│   └── notification_service.py  # Email & in-app notifications
├── integrations/
│   ├── attendance_integration.py  # Attendance system sync
│   └── payroll_integration.py     # Payroll deduction data
├── dashboard/
│   └── dashboard_service.py # Dashboard widgets & stats
├── tasks/
│   ├── accrual_tasks.py     # Celery tasks for accrual & expiry
│   └── notification_tasks.py # Async notification delivery
├── serializers/
│   ├── leave_type_serializer.py   # LeaveType list/detail
│   ├── balance_serializer.py      # LeaveBalance with computed fields
│   └── request_serializer.py      # LeaveRequest with permissions
├── filters/
│   └── filters.py           # django-filter FilterSets
├── viewsets/
│   ├── leave_type_viewset.py      # LeaveType CRUD API
│   ├── balance_viewset.py         # Balance read API
│   ├── request_viewset.py         # Request CRUD & workflow actions
│   └── holiday_viewset.py         # Holiday management API
├── admin/
│   └── admin.py             # Django admin configuration
├── management/
│   └── commands/
│       ├── seed_leave_types.py    # Seed Sri Lankan leave types
│       └── seed_holidays.py       # Seed Sri Lankan public holidays
├── constants.py              # Enums: categories, statuses, scopes
├── apps.py                   # Django app config
├── urls.py                   # URL routing
└── migrations/               # Database migrations (0001-0004)
```

## Key Features

- **Sri Lankan Labor Law Compliance**: Pre-configured leave types matching statutory requirements
- **Flexible Policy Engine**: Scope-based policies (ALL, DEPARTMENT, DESIGNATION) with priority resolution
- **Multi-Method Accrual**: Annual grant, monthly accrual, pro-rata for mid-year joiners
- **Carry-Forward with Expiry**: Automatic carry-forward with configurable expiry dates
- **Approval Workflow**: DRAFT → PENDING → APPROVED/REJECTED/CANCELLED, APPROVED → RECALLED
- **Half-Day Support**: First-half or second-half leave with proper validation
- **Holiday Calendar**: Public, bank, company, optional holidays with department scope
- **Working Days Calculation**: Automatic exclusion of weekends and holidays
- **Balance Tracking**: Real-time balance with pending, used, encashed, and carry-forward tracking
- **Team Calendar**: Manager view of team leave schedules
- **Tenant Isolation**: Full multi-tenant support via django-tenants schema separation

## Data Models

### LeaveType

Core configuration for each leave category. Fields include name, code (unique uppercase), category, entitlement days, consecutive day limits, paid/unpaid flag, document requirements, gender restrictions, minimum service months, and notice days.

### LeavePolicy

Links leave types to employee groups with optional entitlement overrides. Supports scope-based targeting (ALL, DEPARTMENT, DESIGNATION) with priority resolution: DESIGNATION > DEPARTMENT > ALL. Time-bound via effective_from/effective_to.

### LeaveBalance

Tracks leave balance per employee, leave type, and calendar year. One record per (employee, leave_type, year) combination. Computed `available_days` property accounts for opening balance, allocated days, carry-forward, usage, pending requests, encashment, and carry-forward expiry.

### LeaveRequest

Employee leave applications with full status workflow. Supports half-day leave, document attachments, and approval tracking. Employee FK uses PROTECT to prevent accidental data loss.

### Holiday

Holiday definitions with scope (ALL, DEPARTMENT, LOCATION), recurrence support, and type classification (PUBLIC, BANK, COMPANY, OPTIONAL).

## Services

### LeaveAccrualService

- `grant_annual_accrual()` — Full annual entitlement at once
- `process_monthly_accrual()` — Monthly credit (annual / 12)
- `calculate_pro_rata()` — Mid-year joiner entitlement
- `process_carry_forward()` — Year-end carry-forward with limits
- `check_and_expire_leaves()` — Expire past-due carry-forward
- `execute_year_end_rollover()` — Full year-end orchestration

### LeaveRequestService

- `create_draft()` — Create leave request in DRAFT status
- `submit()` — Validate balance/overlap, transition to PENDING
- `approve()` — PENDING → APPROVED with balance updates
- `reject()` — PENDING → REJECTED with balance release
- `cancel()` — PENDING → CANCELLED with balance release
- `recall()` — APPROVED → RECALLED with balance reversal
- `validate_balance()` — Check sufficient leave balance
- `check_overlap()` — Detect overlapping active requests

### LeaveCalendarService

- `get_team_calendar()` — Manager's team leave view
- `get_department_calendar()` — Department-wide calendar
- `get_holidays()` — Holiday listing with scope filters
- `calculate_working_days()` — Working days excluding weekends/holidays
- `auto_adjust_leave_days()` — Auto-calculate leave days for requests
- `generate_calendar_json()` — Calendar data for UI rendering

## Status Workflow

```
DRAFT ──→ PENDING ──→ APPROVED ──→ RECALLED
              │
              ├──→ REJECTED
              │
              └──→ CANCELLED
```

Terminal states: CANCELLED, REJECTED, RECALLED.

## Sri Lankan Compliance

| Leave Type | Annual Days | Paid | Notes                            |
| ---------- | ----------- | ---- | -------------------------------- |
| Annual     | 14          | Yes  | Shop & Office Employees Act      |
| Casual     | 7           | Yes  | For urgent personal matters      |
| Sick       | 7           | Yes  | Medical certificate after 2 days |
| Maternity  | 84          | Yes  | Female only, first 2 children    |
| Paternity  | 3           | Yes  | Male only                        |
| No-Pay     | —           | No   | Subject to management approval   |

## Celery Scheduled Tasks

| Task                       | Schedule       | Purpose                       |
| -------------------------- | -------------- | ----------------------------- |
| `year-end-leave-accrual`   | Dec 31, 23:59  | Annual grant & carry-forward  |
| `daily-leave-expiry-check` | Daily at 00:30 | Expire past-due carry-forward |
