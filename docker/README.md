# Docker Configuration

This directory contains Docker configuration files for the LankaCommerce Cloud development environment.

## Directory Structure

```
docker/
├── backend/     # Backend Dockerfile and related files
├── frontend/    # Frontend Dockerfile and related files
├── nginx/       # Nginx reverse proxy configuration
├── postgres/    # PostgreSQL initialization scripts
├── redis/       # Redis configuration
└── scripts/     # Utility scripts
```

## Usage

Development environment is managed via Docker Compose:

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down
```
