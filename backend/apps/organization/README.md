# Organization Module

Manages the organizational structure including **departments**, **designations** (job titles), department memberships, department heads, and the org-chart hierarchy.

## Models

| Model              | Description                                                                                              |
| ------------------ | -------------------------------------------------------------------------------------------------------- |
| `Department`       | Hierarchical department tree (MPTT). Core fields: name, code, status, parent, manager, location, budget. |
| `Designation`      | Job title/position with level, salary range, and reporting structure.                                    |
| `DepartmentMember` | Tracks employee membership in departments with dates and roles.                                          |
| `DepartmentHead`   | Records department head appointments with history.                                                       |

## Services

| Service                    | Key Methods                                                                                                         |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `DepartmentService`        | `create`, `update`, `archive`, `activate`, `move`, `merge`, `search`                                                |
| `DesignationService`       | `create`, `update`, `deactivate`, `activate`, `validate_salary`, `search`                                           |
| `OrgChartService`          | `get_department_tree`, `get_employee_tree`, `generate_orgchart_json`, `get_department_stats`, `get_reporting_chain` |
| `DepartmentCodeGenerator`  | Auto-generates unique `DEPT-XX` codes.                                                                              |
| `DesignationCodeGenerator` | Auto-generates unique designation codes from titles.                                                                |

## API Endpoints

### Departments (`/api/v1/organization/departments/`)

| Method    | Path               | Description                               |
| --------- | ------------------ | ----------------------------------------- |
| GET       | `/`                | List departments (filterable, searchable) |
| POST      | `/`                | Create department                         |
| GET       | `/{id}/`           | Retrieve department                       |
| PUT/PATCH | `/{id}/`           | Update department                         |
| DELETE    | `/{id}/`           | Delete department                         |
| GET       | `/tree/`           | Full department tree                      |
| GET       | `/{id}/children/`  | Direct child departments                  |
| GET       | `/{id}/employees/` | Employees in department                   |
| GET       | `/{id}/path/`      | Path to root                              |
| GET       | `/{id}/stats/`     | Department statistics                     |
| POST      | `/{id}/move/`      | Move to new parent (`{new_parent_id}`)    |
| POST      | `/{id}/merge/`     | Merge into target (`{target_id}`)         |

### Designations (`/api/v1/organization/designations/`)

| Method    | Path                  | Description                     |
| --------- | --------------------- | ------------------------------- |
| GET       | `/`                   | List designations               |
| POST      | `/`                   | Create designation              |
| GET       | `/{id}/`              | Retrieve designation            |
| PUT/PATCH | `/{id}/`              | Update designation              |
| DELETE    | `/{id}/`              | Delete designation              |
| GET       | `/{id}/employees/`    | Employees with this designation |
| GET       | `/{id}/salary-range/` | Salary range info               |
| GET       | `/level-hierarchy/`   | Level hierarchy with counts     |

### Org Chart (`/api/v1/organization/org-chart/`)

| Method | Path                | Description                    |
| ------ | ------------------- | ------------------------------ |
| GET    | `/?type=department` | Department org chart (default) |
| GET    | `/?type=employee`   | Employee reporting tree        |

## Filters

**DepartmentFilter**: `status`, `parent`, `has_parent`, `has_manager`, `has_budget`, `level_gte`, `level_lte`

**DesignationFilter**: `status`, `level`, `department`, `is_manager`, `has_salary_range`

## Signals

- `track_department_transfer`: Creates/closes `DepartmentMember` records when an employee's department FK changes.
- `track_designation_change`: Logs designation changes for audit.

## Validators

- `validate_no_circular_manager`: Prevents circular manager references.
- `validate_department_consistency`: Ensures manager is in same MPTT branch.
