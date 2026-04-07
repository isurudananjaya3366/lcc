# Scripts Directory

## Overview

This directory contains automation and utility scripts for the LankaCommerce Cloud project. Scripts here help streamline development, database operations, deployment, and other common tasks.

## Script Categories

### Development Scripts
Scripts for setting up and managing the local development environment.

| Script | Purpose |
|--------|---------|
| `setup.sh` | Initial project setup |
| `dev.sh` | Start development environment |
| `lint.sh` | Run linting checks |
| `build.sh` | Build production assets |

### Database Scripts
Scripts for database operations and data management.

| Script | Purpose |
|--------|---------|
| `migrate.sh` | Run database migrations |
| `backup.sh` | Database backup |
| `seed.sh` | Seed development data |

### Deployment Scripts
Scripts for production deployment and rollback.

| Script | Purpose |
|--------|---------|
| `deploy.sh` | Production deployment |
| `rollback.sh` | Rollback to previous version |

### Utility Scripts
Helper scripts for miscellaneous tasks.

| Script | Purpose |
|--------|---------|
| `test.sh` | Run test suites |
| `cleanup.sh` | Clean up temporary files |

## Naming Conventions

| Convention | Example | Description |
|------------|---------|-------------|
| **Lowercase** | `setup.sh` | All lowercase names |
| **Hyphenated** | `run-tests.sh` | Use hyphens for multi-word names |
| **Extension** | `*.sh` | Shell scripts use `.sh` |
| **Prefix** | `db-backup.sh` | Category prefix for clarity |

## Usage Guidelines

### Running Scripts

```bash
# Make the script executable (first time only)
chmod +x scripts/<script-name>.sh

# Run a script from the project root
./scripts/<script-name>.sh
```

### Required Permissions
- Scripts should be made executable before running (`chmod +x`).
- Some scripts may require elevated permissions (e.g., Docker-related scripts).

### Environment Requirements
- Ensure the relevant `.env` file is configured before running scripts.
- Some scripts depend on Docker, Node.js, or Python being installed.
- Check each script's header comments for specific requirements.

## Script Documentation Format

Each script should include the following at the top:

```bash
#!/usr/bin/env bash
# ============================================================================
# Script: <script-name>.sh
# Description: <Brief description of what the script does>
# Usage: ./scripts/<script-name>.sh [options]
# Requirements: <List any dependencies>
# Exit Codes:
#   0 - Success
#   1 - General error
# ============================================================================
```
