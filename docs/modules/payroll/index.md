# Payroll & Salary Structure Module

## Overview

The Payroll & Salary Structure module provides comprehensive salary management for the LankaCommerce Cloud POS system. It supports Sri Lankan statutory compliance including EPF (Employees' Provident Fund), ETF (Employees' Trust Fund), and PAYE (Pay-As-You-Earn) tax calculations. The module handles salary component configuration, template-based salary assignment, grade management, employee salary tracking, revision history, and statutory deduction calculations.

## Architecture

```
apps/payroll/
├── models/
│   ├── __init__.py                    # Model exports (11 models)
│   ├── salary_component.py           # SalaryComponent configuration
│   ├── salary_template.py            # SalaryTemplate grouping
│   ├── template_component.py         # TemplateComponent linkage
│   ├── salary_grade.py               # SalaryGrade pay bands
│   ├── employee_salary.py            # EmployeeSalary records
│   ├── employee_salary_component.py  # EmployeeSalaryComponent amounts
│   ├── salary_history.py             # SalaryHistory audit trail
│   ├── epf_settings.py               # EPFSettings rates & ceiling
│   ├── etf_settings.py               # ETFSettings rates
│   ├── paye_slab.py                  # PAYETaxSlab progressive rates
│   └── tax_exemption.py              # TaxExemption relief amounts
├── services/
│   ├── __init__.py
│   ├── salary_service.py             # Template assignment, revision, comparison
│   ├── epf_calculator.py             # EPF contribution calculation
│   ├── etf_calculator.py             # ETF contribution calculation
│   ├── paye_calculator.py            # PAYE tax calculation (progressive slabs)
│   └── export_service.py             # CSV/JSON export
├── serializers/
│   ├── __init__.py
│   ├── component_serializer.py       # SalaryComponent list/detail
│   ├── template_serializer.py        # SalaryTemplate with nested components
│   └── employee_salary_serializer.py # EmployeeSalary with breakdown
├── views/
│   ├── __init__.py
│   ├── component_viewset.py          # SalaryComponent CRUD
│   ├── template_viewset.py           # SalaryTemplate CRUD + component actions
│   └── employee_salary_viewset.py    # EmployeeSalary CRUD + assign/revise/compare
├── management/
│   └── commands/
│       ├── seed_components.py         # 13 default components (5 statutory + 8 common)
│       ├── seed_grades.py             # 6 salary grades (G1-G6)
│       └── seed_tax_slabs.py          # 2024 PAYE slabs + tax exemptions
├── constants.py               # Enums: ComponentType, CalculationType, ComponentCategory, SalaryChangeReason
├── signals.py                 # Auto-create SalaryHistory on basic salary change
├── filters.py                 # django-filter FilterSets
├── admin.py                   # Django admin configuration
├── apps.py                    # Django app config
├── urls.py                    # URL routing (DefaultRouter)
└── migrations/                # Database migrations (0001_initial)
```

## Key Features

- **Sri Lankan Statutory Compliance**: Built-in EPF (8% employee / 12% employer), ETF (3% employer), and PAYE progressive tax calculation
- **Component-Based Salary**: Flexible salary components supporting earnings, deductions, and employer contributions
- **Template System**: Reusable salary templates that group components for quick employee assignment
- **Grade Management**: Salary grades with min/max pay bands and optional template linkage
- **Salary Revision Tracking**: Full audit trail of salary changes with reason codes
- **Progressive Tax Calculation**: 2024 Sri Lankan PAYE slabs (6% to 36%) with tax exemptions
- **EPF/ETF Ceiling Support**: Maximum contribution ceiling for statutory calculations
- **Auto-History**: Signal-based automatic salary history creation on basic salary changes
- **Export Capabilities**: CSV export of current salaries and JSON salary breakdowns
- **Tenant Isolation**: Full multi-tenant support via django-tenants schema separation

## Data Models

### SalaryComponent

Core building block for salary structures. Each component has a unique code (auto-uppercase), type (EARNING, DEDUCTION, EMPLOYER_CONTRIBUTION), category (BASIC, ALLOWANCE, BONUS, STATUTORY, LOAN, TAX, OTHER), and calculation method (FIXED, PERCENTAGE_OF_BASIC, PERCENTAGE_OF_GROSS, FORMULA). Flags control taxability, EPF applicability, and display ordering. Supports soft delete.

### SalaryTemplate

Groups salary components into reusable templates. Each template has a unique code and can be linked to a designation (FK to Organization Designation). Templates can be activated/deactivated and assigned to employees via SalaryService.

### TemplateComponent

Junction model linking templates to components with default values and override settings. Unique constraint on (template, component) prevents duplicate entries. Supports min/max value ranges for overridable components.

### SalaryGrade

Defines pay bands with min/max salary ranges and numbered levels. Optionally linked to a template for automatic salary structure assignment. Useful for standardized pay scales across the organization.

### EmployeeSalary

Links an employee to their current salary record. Tracks basic salary, gross salary (auto-calculated from earning components), effective dates, and current status. Only one salary per employee should be marked `is_current=True` at any time.

### EmployeeSalaryComponent

Individual component amounts for an employee's salary. Linked to both EmployeeSalary and SalaryComponent. Unique constraint on (employee_salary, component) ensures no duplicate component assignments.

### SalaryHistory

Audit trail of salary changes. Records previous and new basic/gross amounts, effective date, change reason (ANNUAL_INCREMENT, PROMOTION, TRANSFER, RESTRUCTURE, CORRECTION, OTHER), and optional remarks.

### EPFSettings

Configurable EPF rates for employee (default 8%) and employer (default 12%) contributions. Supports maximum contribution ceiling and effective dates. Only active settings are used in calculations.

### ETFSettings

Configurable ETF employer rate (default 3%). Uses the same EPF base (EPF-applicable earnings) for calculation. Supports activation/deactivation and effective dates.

### PAYETaxSlab

Progressive tax slabs for PAYE calculation. Each slab defines a tax year, income range (from_amount to to_amount), and applicable rate. The last slab has null to_amount representing unlimited upper bound. 2024 Sri Lankan rates: 6%, 12%, 18%, 24%, 30%, 36%.

### TaxExemption

Monthly and annual tax exemption amounts. Standard exemptions include Personal Relief (LKR 1,200,000/year) and Qualifying Payment (LKR 300,000/year). Used in PAYE calculation to determine taxable income.

## API Endpoints

| Endpoint                                           | Method               | Description                    |
| -------------------------------------------------- | -------------------- | ------------------------------ |
| `/api/v1/payroll/components/`                      | GET                  | List salary components         |
| `/api/v1/payroll/components/`                      | POST                 | Create salary component        |
| `/api/v1/payroll/components/{id}/`                 | GET/PUT/PATCH/DELETE | Component CRUD (soft delete)   |
| `/api/v1/payroll/templates/`                       | GET                  | List salary templates          |
| `/api/v1/payroll/templates/`                       | POST                 | Create salary template         |
| `/api/v1/payroll/templates/{id}/`                  | GET/PUT/PATCH/DELETE | Template CRUD                  |
| `/api/v1/payroll/templates/{id}/add_component/`    | POST                 | Add component to template      |
| `/api/v1/payroll/templates/{id}/remove_component/` | POST                 | Remove component from template |
| `/api/v1/payroll/salaries/`                        | GET                  | List employee salaries         |
| `/api/v1/payroll/salaries/`                        | POST                 | Create employee salary         |
| `/api/v1/payroll/salaries/{id}/`                   | GET/PUT/PATCH/DELETE | Salary CRUD                    |
| `/api/v1/payroll/salaries/{id}/assign/`            | POST                 | Assign template to employee    |
| `/api/v1/payroll/salaries/{id}/revise/`            | POST                 | Revise employee salary         |
| `/api/v1/payroll/salaries/{id}/compare/`           | POST                 | Compare two salary records     |

## Services

### SalaryService

Handles salary lifecycle operations:

- **assign_template**: Creates employee salary from a template with component defaults
- **override_component**: Updates individual component amounts with gross recalculation
- **recalculate_gross**: Sums all earning components to compute gross salary
- **revise_salary**: Creates new salary record, copies components, records history
- **compare_salaries**: Returns detailed component-level differences between two salary records

### EPFCalculator

Calculates EPF contributions based on EPF-applicable earnings:

- Identifies EPF base (sum of EPF-applicable earning components)
- Applies employee rate (8%) and employer rate (12%)
- Respects maximum contribution ceiling when configured

### ETFCalculator

Calculates ETF employer contribution:

- Uses same EPF base calculation
- Applies employer rate (3%)

### PAYECalculator

Calculates progressive income tax:

- Determines monthly taxable income from taxable earning components
- Applies monthly tax exemptions (Personal Relief + Qualifying Payment)
- Annualizes net taxable income for slab calculation
- Applies progressive tax rates across income bands
- Returns monthly tax (annual_tax / 12)

## Management Commands

| Command                            | Description                                                 |
| ---------------------------------- | ----------------------------------------------------------- |
| `python manage.py seed_components` | Seeds 13 default salary components (5 statutory + 8 common) |
| `python manage.py seed_grades`     | Seeds 6 salary grades (G1 Entry through G6 Executive)       |
| `python manage.py seed_tax_slabs`  | Seeds 2024 PAYE tax slabs and 2 standard tax exemptions     |

## Tests

66 tests covering models, services, signals, and calculations:

```bash
docker compose exec backend sh -c 'cd /app && DJANGO_SETTINGS_MODULE=config.settings.test_pg python -m pytest tests/payroll/ -v --tb=short --reuse-db'
```

### Test Coverage

- **Model Tests (37)**: CRUD, unique constraints, soft delete, auto-uppercase codes, ordering, str representations
- **Service Tests (29)**: Template assignment, component override, gross recalculation, salary revision, comparison, EPF/ETF/PAYE calculations, signal-based history creation
