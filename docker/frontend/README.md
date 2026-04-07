# Frontend Docker Configuration

Docker configuration files for the Next.js frontend application.

## Files

- `Dockerfile.dev` - Development Dockerfile with hot reload
- `Dockerfile.prod` - Production Dockerfile with optimizations

## Development Image Features

- Node.js 20 LTS base
- pnpm package manager
- Hot reload enabled
- Development dependencies included

## Production Image Features

- Multi-stage build
- Static assets optimized
- Next.js standalone output
- Minimal final image
