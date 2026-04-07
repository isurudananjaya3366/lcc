# Contributing to LankaCommerce Cloud (LCC)

Thanks for taking the time to contribute! 🎉

This project is being built via an AI-agent-driven document series, but human contributions (code, docs, testing, review) are extremely valuable.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Ways to Contribute](#ways-to-contribute)
3. [Development Setup](#development-setup-local)
4. [Coding Standards](#coding-standards)
5. [Commit Message Conventions](#commit-message-conventions)
6. [Branch Strategy](#branch-strategy)
7. [Pull Request Process](#pull-request-process)
8. [Code Review](#code-review)
9. [Reporting Issues](#reporting-issues)
10. [Security Vulnerabilities](#security-vulnerabilities)
11. [Contact](#contact)

---

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold these standards.

---

## Ways to Contribute

### Code Contributions

- 🐛 Fix bugs — check the [issue tracker](https://github.com/AkbarBeiwormo/pos/issues) for open bugs
- ✨ Implement features — look for issues labeled `enhancement`
- ♻️ Refactor code — improve maintainability and performance
- 🧪 Write tests — increase test coverage

### Documentation

- 📝 Improve existing docs — fix errors, add examples
- 📖 Write guides — tutorials, how-tos, architecture docs
- 💬 Translate docs — help with Sinhala, Tamil, or English localization

### Localization

- 🇱🇰 Sinhala / Tamil translations — UI strings, help text, error messages
- 🔤 Singlish/Sinhala search terms — improve local search accuracy
- 💱 LKR formatting — currency, date, and number localization

### Other

- 🔍 Report bugs — use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- 💡 Suggest features — use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- 🗣️ Participate in discussions — share ideas and feedback

---

## Development Setup (local)

### Prerequisites

- Git
- Docker Desktop
- Python 3.12+
- Node.js 20 LTS
- pnpm (for frontend)

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/<your-username>/pos.git
   cd pos
   ```
3. **Set up the development environment:**

   ```bash
   # Copy environment variables
   cp .env.example .env

   # Start the dev stack
   docker compose up -d
   ```

4. **Backend setup:**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements/local.txt
   ```
5. **Frontend setup:**
   ```bash
   cd frontend
   pnpm install
   pnpm dev
   ```

### Expected Dev URLs

- Backend API: `http://localhost:8000/`
- Frontend: `http://localhost:3000/`
- Timezone: `Asia/Colombo`

---

## Coding Standards

### Python

- Follow PEP 8
- Formatting: Black (target line length 88)
- Linting: Ruff, flake8, mypy
- Prefer type hints where practical
- Use `snake_case` for variables and functions, `PascalCase` for classes

### TypeScript / JavaScript

- Linting: ESLint
- Formatting: Prettier
- Keep components small and testable
- Use `camelCase` for variables and functions, `PascalCase` for components

For detailed standards, see [docs/CODE_REVIEW.md](docs/CODE_REVIEW.md#code-quality-criteria).

---

## Commit Message Conventions

We follow **Conventional Commits**. All commits are validated by commitlint.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type       | Description                           |
| ---------- | ------------------------------------- |
| `feat`     | New feature                           |
| `fix`      | Bug fix                               |
| `docs`     | Documentation only                    |
| `style`    | Formatting only                       |
| `refactor` | Code restructure (no behavior change) |
| `perf`     | Performance improvement               |
| `test`     | Tests                                 |
| `build`    | Build system or dependencies          |
| `ci`       | CI/CD changes                         |
| `chore`    | Maintenance                           |
| `revert`   | Revert a previous commit              |

### Examples

```
feat(pos): add barcode scanning to checkout
fix(inventory): correct stock calculation for bundled products
docs(readme): add Sri Lanka context and quickstart
```

### Interactive Commits

Use Commitizen for guided commit messages:

```bash
npm run commit
```

For full details, see [docs/COMMITS.md](docs/COMMITS.md).

---

## Branch Strategy

We follow a Git Flow-based strategy:

| Branch      | Purpose                                              |
| ----------- | ---------------------------------------------------- |
| `main`      | Stable, always releasable                            |
| `develop`   | Integration branch for features                      |
| `feature/*` | New features (e.g., `feature/add-sinhala-search`)    |
| `fix/*`     | Bug fixes (e.g., `fix/cart-calculation-error`)       |
| `hotfix/*`  | Production hotfixes (e.g., `hotfix/payment-timeout`) |
| `release/*` | Release preparation (e.g., `release/1.2.0`)          |

### Workflow

1. Create your branch from `develop` (features/fixes) or `main` (hotfixes)
2. Make focused, small commits
3. Push to your fork and open a PR
4. PRs merge into `develop`; releases merge into `main`

For full details, see [docs/BRANCHING.md](docs/BRANCHING.md).

---

## Pull Request Process

1. **Create a focused branch** from the appropriate base
2. **Keep changes small** — ideally < 200 lines changed
3. **Add/update tests** for new features and bug fixes
4. **Update documentation** when behavior changes
5. **Ensure all checks pass** — lint, tests, type checks
6. **Open a PR** using the [PR template](.github/PULL_REQUEST_TEMPLATE.md)
7. **Respond to review feedback** within 24 hours

### PR Templates

- Default: [PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)
- Feature: [feature.md](.github/PULL_REQUEST_TEMPLATE/feature.md)
- Bugfix: [bugfix.md](.github/PULL_REQUEST_TEMPLATE/bugfix.md)
- Hotfix: [hotfix.md](.github/PULL_REQUEST_TEMPLATE/hotfix.md)

### Quality Gates

All PRs must pass:

- [ ] Linting (ESLint, Ruff, flake8)
- [ ] Type checking (mypy, TypeScript)
- [ ] Tests (pytest, Jest)
- [ ] At least 1 approval (2 for critical changes)

---

## Code Review

### Review Expectations

- **Initial response:** Within 24 hours (business hours, Asia/Colombo timezone)
- **Complete review:** Within 48 hours for normal PRs
- **Re-review after changes:** Within 8 hours

### What Reviewers Look For

- Correctness and safety (multi-tenant boundaries!)
- Clear naming and structure
- Tests for business-critical flows
- Security (no hardcoded secrets, input validation)
- Performance (no N+1 queries, efficient algorithms)
- Minimal breaking changes

For full review guidelines, see [docs/CODE_REVIEW.md](docs/CODE_REVIEW.md).

---

## Reporting Issues

### Bug Reports

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md). Include:

- Steps to reproduce
- Expected vs actual behavior
- Environment details (browser, OS, tenant)
- Screenshots or logs

### Feature Requests

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md). Include:

- Problem description
- Proposed solution
- User stories and acceptance criteria

### Tasks

Use the [task template](.github/ISSUE_TEMPLATE/task.md) for planned development work.

---

## Security Vulnerabilities

**Do NOT create a public issue for security vulnerabilities.**

Please report security issues privately. See [SECURITY.md](SECURITY.md) for the full disclosure process and reporting instructions.

---

## Contact

- **Security issues:** See [SECURITY.md](SECURITY.md)
- **General inquiries:** `dev@lankacommerce.lk` _(placeholder)_
- **Discussions:** [GitHub Discussions](https://github.com/AkbarBeiwormo/pos/discussions)

---

Thank you for helping make LankaCommerce Cloud better for Sri Lankan businesses! 🇱🇰

### Security issues

Please do **not** open public issues for security vulnerabilities.
Instead, report privately to: `security@lankacommerce.lk` (placeholder)
