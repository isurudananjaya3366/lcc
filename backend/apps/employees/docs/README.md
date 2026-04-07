# Employee Management Module

## Overview

The Employee Management module provides comprehensive employee lifecycle management for the Lanka Commerce POS platform. It handles employee records, addresses, emergency contacts, family members, bank accounts, documents, and employment history tracking.

## Architecture

```
apps/employees/
├── models/
│   ├── employee.py              # Core Employee model
│   ├── employee_address.py      # Employee addresses (permanent, current)
│   ├── employee_bank.py         # Bank account details
│   ├── employee_document.py     # Document uploads & verification
│   ├── employee_family.py       # Family member records
│   ├── emergency_contact.py     # Emergency contacts
│   └── employment_history.py    # Employment change history log
├── services/
│   ├── employee_service.py      # Core business logic (CRUD, lifecycle)
│   ├── id_generator.py          # Employee ID generation (EMP-XXXXX)
│   ├── import_service.py        # Bulk import from Excel/CSV
│   └── search_service.py        # Multi-field search
├── serializers/
│   └── employee_serializer.py   # DRF serializers for all models
├── views/
│   ├── employee_viewset.py      # Employee CRUD + lifecycle actions
│   └── document_viewset.py      # Document upload/download/verify
├── validators/
│   ├── nic_validator.py         # Sri Lankan NIC validation
│   └── phone_validator.py       # Sri Lankan phone validation
├── constants.py                 # Status, type, and choice constants
├── filters.py                   # Django-filter FilterSet classes
├── signals.py                   # Auto-history tracking signals
├── admin.py                     # Django admin configuration
└── urls.py                      # API URL routing
```

## Models

### Employee

Core model with personal details, employment information, and lifecycle fields.

**Key Fields:**

- `employee_id` — Auto-generated unique ID (EMP-XXXXX)
- `nic_number` — Sri Lankan National Identity Card (validated)
- `status` — active, inactive, terminated, resigned, suspended
- `employment_type` — full_time, part_time, contract, intern, temporary, consultant
- `work_location_type` — office, branch, remote, hybrid, field, client_site

**Lifecycle Fields:**

- Probation: `probation_end_date`, `confirmation_date`
- Termination: `termination_date`, `termination_reason`, `termination_notes`, `exit_interview_date`, `terminated_by`, `final_settlement_amount/paid`
- Resignation: `resignation_date`, `resignation_reason`, `notice_period_waived`, `last_working_date`, `counter_offer_made/accepted`, `resignation_letter_received`

### EmployeeAddress

Supports permanent and current addresses with Sri Lankan provinces.

### EmployeeBankAccount

Bank details with masking support (`get_masked_account_number()`), international fields (IBAN, routing number), Sri Lankan bank list.

### EmployeeDocument

Document management with file upload, verification tracking (`is_verified`, `verified_by`, `verified_at`), expiry tracking.

### EmployeeFamily

Family member records with dependent tracking.

### EmergencyContact

Emergency contacts with priority ordering.

### EmploymentHistory

Automatic tracking of employment changes (hire, promotion, demotion, transfer, salary change, status change, manager change, probation confirmation, resignation, termination).

## API Endpoints

### Employee CRUD

| Method | URL                       | Description                            |
| ------ | ------------------------- | -------------------------------------- |
| GET    | `/api/v1/employees/`      | List employees (paginated, filterable) |
| POST   | `/api/v1/employees/`      | Create employee                        |
| GET    | `/api/v1/employees/{id}/` | Retrieve employee detail               |
| PUT    | `/api/v1/employees/{id}/` | Full update                            |
| PATCH  | `/api/v1/employees/{id}/` | Partial update                         |
| DELETE | `/api/v1/employees/{id}/` | Soft delete                            |

### Lifecycle Actions

| Method | URL                                  | Description                |
| ------ | ------------------------------------ | -------------------------- |
| POST   | `/api/v1/employees/{id}/activate/`   | Activate employee          |
| POST   | `/api/v1/employees/{id}/deactivate/` | Deactivate employee        |
| POST   | `/api/v1/employees/{id}/terminate/`  | Terminate employee         |
| POST   | `/api/v1/employees/{id}/resign/`     | Process resignation        |
| POST   | `/api/v1/employees/{id}/link-user/`  | Link platform user account |

### Nested Resources

| Method   | URL                                          | Description               |
| -------- | -------------------------------------------- | ------------------------- |
| GET/POST | `/api/v1/employees/{id}/addresses/`          | List/create addresses     |
| GET/POST | `/api/v1/employees/{id}/emergency-contacts/` | List/create contacts      |
| GET/POST | `/api/v1/employees/{id}/family-members/`     | List/create family        |
| GET/POST | `/api/v1/employees/{id}/documents/`          | List/upload documents     |
| GET/POST | `/api/v1/employees/{id}/bank-accounts/`      | List/create bank accounts |
| GET      | `/api/v1/employees/{id}/history/`            | View employment history   |

### Document Management

| Method | URL                                         | Description         |
| ------ | ------------------------------------------- | ------------------- |
| GET    | `/api/v1/employee-documents/`               | List documents      |
| POST   | `/api/v1/employee-documents/`               | Upload document     |
| GET    | `/api/v1/employee-documents/{id}/download/` | Download file       |
| POST   | `/api/v1/employee-documents/{id}/verify/`   | Mark as verified    |
| POST   | `/api/v1/employee-documents/{id}/unverify/` | Remove verification |
| DELETE | `/api/v1/employee-documents/{id}/`          | Soft delete         |

## Filtering & Search

### Employee Filters

- `status` — Filter by employee status
- `employment_type` — Filter by employment type
- `gender` — Filter by gender
- `department` — Filter by department
- `designation` — Filter by designation
- `hired_after` / `hired_before` — Date range for hire date
- `has_user_account` — Boolean filter for linked user accounts
- `is_on_probation` — Boolean filter for probation status
- `manager` — Filter by manager UUID
- `search` — Multi-field text search (name, email, NIC, employee ID)

### Document Filters

- `employee` — Filter by employee
- `document_type` — Filter by document type
- `is_sensitive` — Filter sensitive documents
- `visible_to_employee` — Filter visibility
- `expiring_within_days` — Filter documents expiring within N days

## Sri Lankan Localizations

### NIC Validation

- Old format: 9 digits + V/X (e.g., `912345678V`)
- New format: 12 digits (e.g., `199123456789`)
- Extracts birth year and gender from NIC
- Validates day-of-year range and year-not-in-future

### Phone Validation

- Validates Sri Lankan mobile and landline numbers
- Supports `+94` country code and `0` local prefix
- Validates mobile prefixes (70-78) and area codes (11-91)

### Bank List

29 Sri Lankan banks with codes for bank account validation.

## Status Transitions

```
active → inactive, terminated, resigned, suspended
inactive → active, terminated
suspended → active, terminated
```

## Signals & Auto-tracking

The module automatically tracks:

- **Hire**: Creates HIRE history entry when new employee is saved
- **Status changes**: Tracks all lifecycle transitions
- **Manager changes**: Logs MANAGER_CHANGE when reporting_to changes
- **Confirmation**: Logs PROBATION_CONFIRMATION when confirmation_date is set
- **Department/designation transfers**: Logged by service layer

## Configuration

### Pagination

- Default page size: 25
- Maximum page size: 100
- Query param: `page_size`

### Retirement Age

- Default: 60 (configurable via `RETIREMENT_AGE` constant)
