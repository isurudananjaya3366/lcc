# Attendance Module API Documentation

## Overview

The Attendance module provides comprehensive attendance tracking including shift management,
clock-in/clock-out, regularization workflows, overtime management, and reporting.

**Base URL:** `/api/v1/attendance/`

---

## Endpoints

### Shifts

| Method | Endpoint                   | Description             |
| ------ | -------------------------- | ----------------------- |
| GET    | `/shifts/`                 | List all shifts         |
| POST   | `/shifts/`                 | Create a new shift      |
| GET    | `/shifts/{id}/`            | Retrieve shift details  |
| PUT    | `/shifts/{id}/`            | Full update a shift     |
| PATCH  | `/shifts/{id}/`            | Partial update a shift  |
| DELETE | `/shifts/{id}/`            | Soft delete a shift     |
| POST   | `/shifts/{id}/activate/`   | Activate a shift        |
| POST   | `/shifts/{id}/deactivate/` | Deactivate a shift      |
| GET    | `/shifts/active/`          | List active shifts only |

**Filters:** `shift_type`, `status`, `is_default`, `start_time_gte`, `start_time_lte`, `work_hours_gte`, `work_hours_lte`  
**Search:** `name`, `code`, `description`  
**Ordering:** `name`, `code`, `start_time`, `work_hours`, `created_on`

---

### Attendance Records

| Method | Endpoint                  | Description             |
| ------ | ------------------------- | ----------------------- |
| GET    | `/records/`               | List attendance records |
| POST   | `/records/`               | Create a record (admin) |
| GET    | `/records/{id}/`          | Retrieve record details |
| PUT    | `/records/{id}/`          | Update a record         |
| PATCH  | `/records/{id}/`          | Partial update          |
| DELETE | `/records/{id}/`          | Soft delete             |
| GET    | `/records/my-attendance/` | Current user's records  |
| GET    | `/records/today/`         | Today's summary         |
| GET    | `/records/summary/`       | Date-range summary      |
| GET    | `/records/export/`        | CSV export              |

**Filters:** `employee`, `shift`, `status`, `date`, `date_from`, `date_to`, `is_late`, `is_early_leave`, `has_overtime`, `department`  
**Search:** `employee__first_name`, `employee__last_name`, `employee__employee_id`  
**Ordering:** `date`, `clock_in`, `clock_out`, `status`, `work_hours`, `created_on`

---

### Clock In / Clock Out

| Method | Endpoint         | Description                      |
| ------ | ---------------- | -------------------------------- |
| POST   | `/check-in/`     | Clock in for today               |
| POST   | `/check-out/`    | Clock out for today              |
| GET    | `/check-status/` | Current user's attendance status |

**Clock-in Payload:**

```json
{
  "shift_id": "uuid (optional)",
  "clock_in_method": "web|mobile|biometric",
  "location": { "latitude": 6.9271, "longitude": 79.8612 },
  "notes": "optional notes"
}
```

**Clock-out Payload:**

```json
{
  "clock_out_method": "web|mobile|biometric",
  "location": { "latitude": 6.9271, "longitude": 79.8612 },
  "notes": "optional notes"
}
```

---

### Regularizations

| Method | Endpoint                         | Description           |
| ------ | -------------------------------- | --------------------- |
| GET    | `/regularizations/`              | List requests         |
| POST   | `/regularizations/`              | Create a request      |
| GET    | `/regularizations/{id}/`         | Retrieve details      |
| PUT    | `/regularizations/{id}/`         | Update request        |
| DELETE | `/regularizations/{id}/`         | Delete request        |
| POST   | `/regularizations/{id}/approve/` | Approve request       |
| POST   | `/regularizations/{id}/reject/`  | Reject request        |
| GET    | `/regularizations/pending/`      | List pending requests |

**Filters:** `employee`, `status`, `date_from`, `date_to`

---

### Overtime Requests

| Method | Endpoint                           | Description           |
| ------ | ---------------------------------- | --------------------- |
| GET    | `/overtime-requests/`              | List requests         |
| POST   | `/overtime-requests/`              | Create a request      |
| GET    | `/overtime-requests/{id}/`         | Retrieve details      |
| PUT    | `/overtime-requests/{id}/`         | Update request        |
| DELETE | `/overtime-requests/{id}/`         | Delete request        |
| POST   | `/overtime-requests/{id}/approve/` | Approve request       |
| POST   | `/overtime-requests/{id}/reject/`  | Reject request        |
| GET    | `/overtime-requests/pending/`      | List pending requests |

**Filters:** `employee`, `status`, `date`, `date_from`, `date_to`

---

### Biometric Webhook

| Method | Endpoint              | Description              |
| ------ | --------------------- | ------------------------ |
| POST   | `/webhook/biometric/` | Receive biometric events |

**Payload:**

```json
{
  "device_id": "DEVICE-001",
  "event_type": "PUNCH_IN|PUNCH_OUT|check_in|check_out",
  "employee_biometric_id": "BIO12345",
  "timestamp": "2026-01-24T08:00:00Z",
  "location": { "latitude": 6.9271, "longitude": 79.8612 }
}
```

---

## Models

- **Shift** — Work shift configuration with time rules and overtime settings
- **ShiftSchedule** — Employee/department shift assignments with weekday patterns
- **AttendanceRecord** — Daily attendance record with clock in/out and computed hours
- **AttendanceRegularization** — Request to correct an attendance record
- **OvertimeRequest** — Pre/post-approval overtime request
- **AttendanceSettings** — Tenant-level attendance configuration

## Services

- **AttendanceService** — Clock in/out, shift lookup, late/early detection
- **BiometricIntegrationService** — Process biometric device events
- **MobileCheckInService** — GPS-verified mobile check-in with geofencing
- **RegularizationService** — Create/approve/reject regularization workflow
- **OvertimeService** — Detect, calculate, and manage overtime
- **AttendanceReportService** — Daily/weekly/monthly/department reports
- **AttendanceExportService** — CSV exports for attendance data

## Celery Tasks

- **mark_daily_absent** — Marks absent employees at end of day (all tenants)
- **auto_clock_out** — Auto-closes open attendance records at configured time
