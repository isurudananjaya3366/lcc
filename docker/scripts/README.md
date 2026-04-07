# Docker Utility Scripts

Utility scripts for managing Docker containers and services.

## Scripts

### Container Management

- `wait-for-it.sh` - Wait for service availability
- `healthcheck.sh` - Container health check script

### Database Management

- `backup-db.sh` - Backup PostgreSQL database
- `restore-db.sh` - Restore database from backup

### Development Helpers

- `reset-dev.sh` - Reset development environment
- `seed-data.sh` - Seed development data

## Usage

Scripts are mounted into containers or run from host:

```bash
# Run from host
./docker/scripts/reset-dev.sh

# Inside container
/scripts/healthcheck.sh
```

## Making Scripts Executable

```bash
chmod +x docker/scripts/*.sh
```
