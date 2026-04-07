# Backend Docker Configuration

Docker configuration files for the Django backend application.

## Files

- `Dockerfile.dev` - Development Dockerfile with hot reload
- `Dockerfile.prod` - Production Dockerfile with optimizations
- `entrypoint.sh` - Container entrypoint script
- `start-dev.sh` - Development server startup script

## Development Image Features

- Python 3.12 base
- Hot reload with Watchdog
- Debug mode enabled
- Development dependencies included

## Production Image Features

- Multi-stage build
- Minimal dependencies
- Gunicorn WSGI server
- Static files collected
