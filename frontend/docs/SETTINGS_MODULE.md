# Settings Module Documentation

## 1. Overview

The Settings module provides a comprehensive admin configuration interface for the LankaCommerce Cloud POS system. It covers account preferences, company profile, user/role management, third-party integrations, API key management, billing/subscription handling, and audit logging.

### Technology Stack

- **Framework:** Next.js 15 (App Router)
- **UI:** shadcn/ui + Tailwind CSS
- **Forms:** React Hook Form + Zod
- **Tables:** TanStack Table v8
- **State:** React useState (local), TanStack Query (server)
- **Icons:** Lucide React

---

## 2. Routes & Navigation

| Route | Page | Description |
|-------|------|-------------|
| `/settings` | General Settings | Timezone, currency, date format, notifications |
| `/settings/company` | Company Profile | Name, logo, address, tax, contact |
| `/settings/users` | User Management | Invite, edit, disable, remove users |
| `/settings/roles` | Roles & Permissions | Create roles, manage permissions matrix |
| `/settings/roles/[id]` | Edit Role | Edit existing role with permissions |
| `/settings/integrations` | Integrations | Connect/manage third-party services |
| `/settings/api-keys` | API Keys | Generate, view, revoke API keys |
| `/settings/billing` | Billing & Plans | Subscription, invoices, payment methods |
| `/settings/audit-log` | Audit Log | System activity tracking and filtering |

### Layout Structure

- **Desktop (≥1024px):** Two-column layout with fixed 256px sidebar + content area
- **Mobile (<1024px):** Full-width content with floating drawer button for navigation
- **Sidebar:** Sticky positioning, divided into Account and System sections

---

## 3. Features

### General Settings
- Timezone selection (default: Asia/Colombo UTC+5:30)
- Currency selection (default: LKR - Sri Lankan Rupees)
- Date format selection (default: DD/MM/YYYY)
- Notification preferences: Email, Push, Order Alerts, Low Stock Alerts, Daily Reports

### Company Settings
- Company name with validation (2-200 chars)
- Logo upload with drag-and-drop (PNG/JPG/SVG, max 2MB)
- Logo preview with view and remove actions
- Sri Lankan address form (street, city, 9 provinces, 5-digit postal code)
- Tax information (TIN, VAT number, registration type)
- Contact info (phone: +94XXXXXXXXX, email, website)
- Zod schema validation with dirty state detection

### User Management
- User invitation via email with role assignment
- User table with sorting, pagination (TanStack Table)
- Status badges: Active (green), Pending (amber), Disabled (red)
- Edit user role, disable/enable toggle
- Remove user with DELETE confirmation typing
- Pending invitations with resend/cancel

### Roles & Permissions
- Role cards in responsive grid (1/2/3 columns)
- 31 permissions across 10 modules
- Permission matrix with select-all and indeterminate state
- Add/edit/delete roles with validation
- System role protection (cannot delete)
- Delete requires typing role name confirmation

### Integrations
- Integration cards grouped by category (Payment, Communication, Business, Other)
- Status: Connected, Disconnected, Error
- Settings modal with API key, secret, webhook URL
- Test connection and disconnect with confirmation
- 6 pre-configured integrations (PayHere, Dialog SMS, Xero, etc.)

### API Keys
- Generate new keys with name and description
- One-time key display with copy and visibility toggle
- Security warning for key storage
- Keys table with masked display
- Revoke with confirmation dialog

### Billing & Plans
- Current plan card with LKR pricing
- 4 plan tiers: Starter (Free), Business (₨4,999/mo), Pro (₨9,999/mo), Enterprise (Custom)
- Monthly/Annual billing toggle (20% annual discount)
- Feature comparison across tiers
- Billing history table with invoice download
- Payment method management (add/remove/set default)

### Audit Log
- Activity tracking with relative timestamps
- Color-coded action badges (Create/Update/Delete/Login/Logout/Permission/Settings/System)
- Expandable row details (entity ID, IP address, full timestamp)
- Filters: User, Action, Entity Type, Date Range, Search
- Active filter badges with clear functionality

---

## 4. Component Structure

```
components/modules/settings/
├── Layout/
│   ├── SettingsLayout.tsx       # Two-column layout with mobile drawer
│   ├── SettingsSidebar.tsx      # Navigation sidebar (8 items, 2 sections)
│   └── index.ts
├── General/
│   ├── SettingsSectionCard.tsx  # Reusable section wrapper
│   ├── TimezoneSelect.tsx      # Timezone dropdown
│   ├── CurrencySelect.tsx      # Currency dropdown
│   ├── DateFormatSelect.tsx    # Date format dropdown
│   ├── LocalizationSettings.tsx # Localization section
│   ├── NotificationSettings.tsx # Notification toggles
│   ├── GeneralSettings.tsx     # Page container
│   └── index.ts
├── Company/
│   ├── LogoUpload.tsx          # Drag-and-drop upload
│   ├── LogoPreview.tsx         # Preview with view/remove
│   ├── CompanyNameInput.tsx    # Name form field
│   ├── CompanyAddressForm.tsx  # Address with provinces
│   ├── TaxInfoSection.tsx      # Tax ID, VAT, registration
│   ├── ContactInfoSection.tsx  # Phone, email, website
│   ├── CompanySettings.tsx     # Page container with form
│   └── index.ts
├── Users/
│   ├── UserStatusBadge.tsx     # Active/Pending/Disabled
│   ├── UserActionsCell.tsx     # Row actions dropdown
│   ├── UserTableColumns.tsx    # Column definitions
│   ├── UsersTable.tsx          # TanStack Table
│   ├── UsersHeader.tsx         # Title + invite button
│   ├── InviteUserModal.tsx     # Invite form
│   ├── EditUserModal.tsx       # Edit role modal
│   ├── DisableUserAction.tsx   # Enable/disable toggle
│   ├── RemoveUserDialog.tsx    # DELETE confirmation
│   ├── PendingInvitations.tsx  # Pending invites list
│   ├── UsersPage.tsx           # Page container
│   └── index.ts
├── Roles/
│   ├── RoleUserCount.tsx       # User count display
│   ├── RoleActions.tsx         # Edit/Delete actions
│   ├── RoleCard.tsx            # Role card component
│   ├── RolesList.tsx           # Responsive grid
│   ├── PermissionCheckbox.tsx  # Single permission
│   ├── PermissionGroup.tsx     # Group with select-all
│   ├── PermissionMatrix.tsx    # Full permissions grid
│   ├── RoleNameInput.tsx       # Name form field
│   ├── RoleDescriptionInput.tsx # Description with counter
│   ├── AddRoleModal.tsx        # Create role form
│   ├── DeleteRoleDialog.tsx    # Name confirmation delete
│   ├── RolesHeader.tsx         # Title + add button
│   ├── RolesPage.tsx           # Page container
│   └── index.ts
├── Integrations/
│   ├── IntegrationStatus.tsx   # Status badge (3 states)
│   ├── IntegrationCard.tsx     # Integration display
│   ├── IntegrationsGrid.tsx    # Grouped grid layout
│   ├── IntegrationSettingsModal.tsx # Settings/disconnect
│   ├── IntegrationsPage.tsx    # Page container
│   └── index.ts
├── APIKeys/
│   ├── APIKeyDisplay.tsx       # Key display with copy
│   ├── RevokeKeyAction.tsx     # Revoke confirmation
│   ├── GenerateKeyModal.tsx    # Generate new key
│   ├── APIKeysTable.tsx        # Keys table
│   ├── APIKeysPage.tsx         # Page container
│   └── index.ts
├── Billing/
│   ├── PlanFeaturesList.tsx    # Features with ✓/✗
│   ├── CurrentPlanCard.tsx     # Current plan display
│   ├── PlanSelectionModal.tsx  # Plan comparison/select
│   ├── BillingHistoryTable.tsx # Invoice history
│   ├── DownloadInvoice.tsx     # Invoice download
│   ├── PaymentMethodSection.tsx # Payment cards
│   ├── AddPaymentMethodModal.tsx # Add card form
│   ├── BillingPage.tsx         # Page container
│   └── index.ts
├── AuditLog/
│   ├── AuditLogFilters.tsx     # Filter controls
│   ├── AuditLogTable.tsx       # Log entries table
│   ├── AuditLogPage.tsx        # Page container
│   └── index.ts
└── index.ts                    # Top-level barrel exports
```

---

## 5. API Endpoints (Backend Integration Points)

### General Settings
- `GET /api/settings/general` — Get current settings
- `PUT /api/settings/general` — Update settings

### Company Settings
- `GET /api/settings/company` — Get company profile
- `PUT /api/settings/company` — Update company profile
- `POST /api/settings/company/logo` — Upload company logo

### User Management
- `GET /api/settings/users` — List users
- `POST /api/settings/users/invite` — Send invitation
- `PUT /api/settings/users/{id}` — Update user role
- `PATCH /api/settings/users/{id}/disable` — Disable/enable user
- `DELETE /api/settings/users/{id}` — Remove user
- `POST /api/settings/users/invitations/{id}/resend` — Resend invitation
- `DELETE /api/settings/users/invitations/{id}` — Cancel invitation

### Roles & Permissions
- `GET /api/settings/roles` — List roles
- `POST /api/settings/roles` — Create role
- `GET /api/settings/roles/{id}` — Get role details
- `PUT /api/settings/roles/{id}` — Update role
- `DELETE /api/settings/roles/{id}` — Delete role
- `GET /api/settings/permissions` — List all permissions

### Integrations
- `GET /api/integrations` — List integrations
- `POST /api/integrations/{id}/connect` — Connect integration
- `DELETE /api/integrations/{id}/disconnect` — Disconnect integration
- `PATCH /api/integrations/{id}/settings` — Update settings
- `POST /api/integrations/{id}/test` — Test connection

### API Keys
- `GET /api/api-keys` — List API keys
- `POST /api/api-keys/generate` — Generate new key
- `DELETE /api/api-keys/{id}` — Revoke key

### Billing
- `GET /api/billing/subscription` — Get current plan
- `POST /api/billing/upgrade` — Upgrade plan
- `POST /api/billing/cancel` — Cancel subscription
- `GET /api/billing/history` — Billing history
- `GET /api/billing/invoices/{id}/download` — Download invoice PDF
- `GET /api/billing/payment-methods` — List payment methods
- `POST /api/billing/payment-methods` — Add payment method
- `POST /api/billing/payment-methods/{id}/set-default` — Set default
- `DELETE /api/billing/payment-methods/{id}` — Remove payment method

### Audit Log
- `GET /api/audit-log` — List audit entries with filter params

---

## 6. Sri Lanka Specific Defaults

| Setting | Default Value |
|---------|--------------|
| Timezone | Asia/Colombo (UTC+5:30) |
| Currency | LKR (Sri Lankan Rupees) |
| Date Format | DD/MM/YYYY |
| Phone Format | +94XXXXXXXXX |
| Postal Code | 5 digits |
| Provinces | 9 (Western, Central, Southern, Northern, Eastern, North Western, North Central, Uva, Sabaragamuwa) |
| Country | Sri Lanka (fixed) |
| Tax Types | Not Registered, VAT Registered, Income Tax Only, Both |

---

## 7. Validation Schemas

### Company Form (`lib/validations/company.ts`)
- `companyFormSchema`: Full company profile validation
- `companyAddressSchema`: Address validation (nested)

### User Invite (`lib/validations/user-invite.ts`)
- `inviteUserSchema`: Email + roleId + optional message (max 500)

### Role (`lib/validations/role.ts`)
- `roleSchema`: Name (2-50) + description (max 200) + permissions array

### Payment Method (`Billing/AddPaymentMethodModal.tsx`)
- `addPaymentMethodSchema`: Card number, expiry, CVC, cardholder name

---

## 8. Type Definitions (`types/settings.ts`)

- `GeneralSettings` — Localization + notification preferences
- `CompanyAddress` — Sri Lankan address structure
- `CompanySettings` — Full company profile
- `TenantUser` — User with role and status
- `UserInvitation` — Pending invitation
- `Role` — Role with permissions and metadata
- `Permission` — Individual permission
- `Integration` — Third-party service connection
- `APIKey` — API key with lifecycle info
- `SubscriptionPlan` — Billing plan details
- `BillingInvoice` — Invoice record
- `PaymentMethod` — Payment card info
- `AuditLogEntry` — Audit trail record
