# POS Module Documentation

Comprehensive documentation for the LankaCommerce POS (Point of Sale) interface module.

## Documents

| #   | Document                                 | Description                                          |
| --- | ---------------------------------------- | ---------------------------------------------------- |
| 1   | [Architecture](01_Architecture.md)       | System design, component hierarchy, state management |
| 2   | [Components](02_Components.md)           | Component reference with props and responsibilities  |
| 3   | [Workflows](03_Workflows.md)             | Sale, payment, shift, and hold/retrieve workflows    |
| 4   | [API Integration](04_API_Integration.md) | Endpoints, request/response formats, error handling  |
| 5   | [User Guide](05_User_Guide.md)           | How to use the POS, keyboard shortcuts               |
| 6   | [Developer Guide](06_Developer_Guide.md) | Setup, development workflow, adding features         |
| 7   | [Troubleshooting](07_Troubleshooting.md) | Common issues and solutions                          |

## Testing

| Document                                      | Description                 |
| --------------------------------------------- | --------------------------- |
| [Testing Checklist](Testing_Checklist.md)     | Feature test scenarios      |
| [Bug Report Template](Bug_Report_Template.md) | Standard bug report format  |
| [Known Issues](Known_Issues.md)               | Known bugs with workarounds |

## Quick Start

```bash
# Start development
cd frontend
pnpm dev

# Access POS
http://localhost:3000/pos

# Run TypeScript check
npx tsc --noEmit
```

## Keyboard Shortcuts

| Key       | Action                      |
| --------- | --------------------------- |
| F2        | Focus search                |
| F3        | Pay                         |
| F4        | Hold sale                   |
| F5        | Retrieve held sale          |
| Escape    | Close modal / Clear search  |
| P         | Print receipt               |
| E         | Email receipt               |
| N / Enter | New sale (in receipt modal) |
