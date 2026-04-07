# Payroll Module — Salary Structure

## Overview

The Payroll module provides comprehensive salary management for the LankaCommerce ERP system, including salary components, templates, grades, employee salary assignment, statutory calculations (EPF, ETF, PAYE), and export capabilities compliant with Sri Lankan labour law.

## Module Structure

```
apps/payroll/
├── models/
│   ├── salary_component.py       # Salary component definitions
│   ├── salary_template.py        # Reusable salary templates
│   ├── template_component.py     # Template-component relationships
│   ├── salary_grade.py           # Salary grade/band definitions
│   ├── employee_salary.py        # Employee salary records
│   ├── employee_salary_component.py  # Per-employee component values
│   ├── salary_history.py         # Salary change audit log
│   ├── epf_settings.py           # EPF configuration
│   ├── etf_settings.py           # ETF configuration
│   ├── paye_slab.py              # PAYE tax slabs
│   └── tax_exemption.py          # Tax exemptions/reliefs
├── services/
│   ├── salary_service.py         # Core salary operations
│   ├── epf_calculator.py         # EPF calculation service
│   ├── etf_calculator.py         # ETF calculation service
│   ├── paye_calculator.py        # PAYE tax calculation
│   └── export_service.py         # Salary data export
├── serializers/                  # DRF serializers
├── views/                        # DRF viewsets
├── admin.py                      # Django admin configuration
├── urls.py                       # API URL routing
├── constants.py                  # Enums and constants
├── filters.py                    # API filters
├── signals.py                    # Signal handlers
└── management/commands/
    ├── seed_grades.py            # Seed salary grades
    ├── seed_tax_slabs.py         # Seed PAYE tax slabs
    └── seed_tax_exemptions.py    # Seed tax exemptions
```

## Key Concepts

### Salary Components

Components are the building blocks of salary — each represents an earning (e.g., Basic Salary, Transport Allowance) or deduction (e.g., EPF Employee, Loan Deduction). Components define:

- **Type**: EARNING, DEDUCTION, or EMPLOYER_CONTRIBUTION
- **Category**: BASIC, ALLOWANCE, BONUS, STATUTORY, OTHER
- **Calculation**: FIXED, PERCENTAGE_OF_BASIC, PERCENTAGE_OF_GROSS
- **Statutory flags**: `is_taxable`, `is_epf_applicable`, `is_fixed`

### Salary Templates

Templates bundle components into reusable structures. A "Standard Staff" template might include Basic, Transport, Medical, and EPF components. Templates can be assigned to employees to set up their salary structure.

### Salary Grades

Grades define salary bands with min/max salary ranges (e.g., G1: LKR 35,000–75,000). Grades can be linked to employee salaries for standardized pay scales.

### Employee Salary

Represents a specific employee's active salary record, linking an employee to a template and containing the actual component amounts, gross salary, and effective dates.

## Statutory Calculations (Sri Lanka)

### EPF (Employees' Provident Fund)

- **Employee contribution**: 8% of EPF-applicable earnings
- **Employer contribution**: 12% of EPF-applicable earnings
- Governed by EPF Act No. 15 of 1958
- Configurable via `EPFSettings` model

### ETF (Employees' Trust Fund)

- **Employer contribution**: 3% of ETF-applicable earnings (same base as EPF)
- Governed by ETF Act No. 46 of 1980
- Configurable via `ETFSettings` model

### PAYE (Pay As You Earn)

Progressive tax on annual taxable income (2024 rates):

| Slab | Annual Income Range (LKR) | Rate |
| ---- | ------------------------- | ---- |
| 0    | 0 – 1,200,000             | 0%   |
| 1    | 1,200,001 – 1,700,000     | 6%   |
| 2    | 1,700,001 – 2,200,000     | 12%  |
| 3    | 2,200,001 – 2,700,000     | 18%  |
| 4    | 2,700,001 – 3,200,000     | 24%  |
| 5    | 3,200,001 – 3,700,000     | 30%  |
| 6    | 3,700,001+                | 36%  |

Tax exemptions include Personal Relief (LKR 1,200,000/year), Spouse Relief, Child Relief, and Disabled Child Relief.

## API Endpoints

| Method | Endpoint                                         | Description                    |
| ------ | ------------------------------------------------ | ------------------------------ |
| GET    | `/api/payroll/components/`                       | List salary components         |
| POST   | `/api/payroll/components/`                       | Create component               |
| GET    | `/api/payroll/templates/`                        | List salary templates          |
| POST   | `/api/payroll/templates/`                        | Create template                |
| POST   | `/api/payroll/templates/{id}/add-component/`     | Add component to template      |
| DELETE | `/api/payroll/templates/{id}/remove-component/`  | Remove component from template |
| GET    | `/api/payroll/salaries/`                         | List employee salaries         |
| POST   | `/api/payroll/salaries/assign/`                  | Assign template to employee    |
| POST   | `/api/payroll/salaries/revise/`                  | Revise employee salary         |
| GET    | `/api/payroll/salaries/{id}/compare/`            | Compare with previous salary   |
| POST   | `/api/payroll/salaries/{id}/override-component/` | Override component amount      |
| GET    | `/api/payroll/salaries/current/`                 | List current salaries only     |
| GET    | `/api/payroll/salaries/export/`                  | Export salaries as CSV         |

## Common Workflows

### New Employee Salary Setup

1. Select or create a salary template
2. Call `POST /salaries/assign/` with employee ID, template ID, and basic salary
3. System creates EmployeeSalary, copies template components, calculates gross

### Annual Salary Revision

1. Call `POST /salaries/revise/` with employee ID, new basic salary, effective date, and reason
2. System closes old salary, creates new one with updated components, logs history

### Component Override

1. Call `POST /salaries/{id}/override-component/` with component ID and new amount
2. System updates the specific component and recalculates gross

## Management Commands

```bash
# Seed default salary grades (G1-G8)
python manage.py seed_grades

# Seed 2024 PAYE tax slabs
python manage.py seed_tax_slabs

# Seed default tax exemptions
python manage.py seed_tax_exemptions
```
