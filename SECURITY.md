# Security Policy

> LankaCommerce Cloud - Security Vulnerability Disclosure Policy

## Supported Versions

| Version                | Supported                |
| ---------------------- | ------------------------ |
| Latest release         | ✅ Active support        |
| Previous minor release | ✅ Security patches only |
| Older releases         | ❌ No longer supported   |

We provide security patches for the latest release and the previous minor release. Older versions should be upgraded to receive security fixes.

---

## Reporting a Vulnerability

**⚠️ Do NOT create a public GitHub issue for security vulnerabilities.**

### How to Report

Please report security vulnerabilities through one of these private channels:

1. **GitHub Security Advisories** _(preferred)_:
   - Navigate to the [Security Advisories page](https://github.com/AkbarBeiwormo/pos/security/advisories/new)
   - Create a new private security advisory

2. **Email:**
   - Send details to: `security@lankacommerce.lk` _(placeholder)_
   - Use the subject line: `[SECURITY] Brief description of vulnerability`

### What to Include

When reporting a vulnerability, please provide:

- **Description:** Clear description of the vulnerability
- **Impact:** What could an attacker do with this vulnerability?
- **Affected component:** Which part of the system is affected?
- **Reproduction steps:** Step-by-step instructions to reproduce
- **Environment:** Version, tenant type, browser (if applicable)
- **Proof of concept:** Code or screenshots demonstrating the issue
- **Suggested fix:** If you have one (optional)

---

## Response Timeline

| Stage                              | Expected Time                   |
| ---------------------------------- | ------------------------------- |
| **Acknowledgment**                 | Within 48 hours                 |
| **Initial assessment**             | Within 72 hours                 |
| **Triage and priority assignment** | Within 5 business days          |
| **Fix development**                | Depends on severity (see below) |
| **Patch release**                  | Coordinated with reporter       |
| **Public disclosure**              | After patch is released         |

### Fix Timeline by Severity

| Severity         | Fix Timeline           |
| ---------------- | ---------------------- |
| 🔴 Critical (P0) | Within 24-48 hours     |
| 🟠 High (P1)     | Within 1 week          |
| 🟡 Medium (P2)   | Within 2 weeks         |
| 🟢 Low (P3)      | Next scheduled release |

---

## Disclosure Process

We follow a **coordinated disclosure** approach:

### 1. Report Received

- Reporter submits vulnerability through a private channel
- We acknowledge receipt within 48 hours

### 2. Triage

- Security team assesses severity and impact
- Priority assigned (P0-P3)
- Reporter notified of assessment

### 3. Remediation

- Fix developed and tested in private
- Reporter invited to verify the fix (optional)
- Patch prepared for release

### 4. Release

- Security patch released
- Advisory published with details
- Affected users notified

### 5. Public Disclosure

- Full details published after patch availability
- Minimum 7 days between patch release and full disclosure
- Reporter credited (with permission)

---

## Multi-Tenant Security

LankaCommerce Cloud is a multi-tenant platform. We take tenant isolation extremely seriously:

- **Cross-tenant data access** vulnerabilities are treated as **Critical (P0)**
- **Tenant context bypass** vulnerabilities are treated as **Critical (P0)**
- **Schema isolation** issues are treated as **High (P1)** minimum

If you discover any issue that could allow one tenant to access another tenant's data, please report it immediately.

---

## Scope

### In Scope

- LankaCommerce Cloud application code (backend and frontend)
- API endpoints and authentication/authorization
- Multi-tenant isolation and schema separation
- Data exposure or leakage between tenants
- Payment processing security
- Session management and token handling
- Input validation and injection vulnerabilities

### Out of Scope

- Third-party services and dependencies (report to their maintainers)
- Social engineering attacks
- Physical attacks
- Denial of service (DoS) attacks on shared infrastructure
- Issues in non-supported versions
- Already known/reported issues

---

## Acknowledgment and Credit

We believe in recognizing the efforts of security researchers:

- **Hall of Fame:** Reporters will be credited in our security acknowledgments (with permission)
- **Attribution:** Security advisories will credit the reporter (unless anonymity is requested)
- **Response:** We will keep reporters informed throughout the remediation process

---

## Contact

- **Security reports:** `security@lankacommerce.lk` _(placeholder)_
- **GitHub Security Advisories:** [Create advisory](https://github.com/AkbarBeiwormo/pos/security/advisories/new)
- **General inquiries:** `dev@lankacommerce.lk` _(placeholder)_

---

Thank you for helping keep LankaCommerce Cloud and our users safe! 🔒
