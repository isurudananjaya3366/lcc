# Nginx Docker Configuration

Reverse proxy configuration for production deployments.

## Directory Structure

```
nginx/
├── conf.d/               # Server block configurations
│   └── default.conf      # Main site configuration
├── nginx.conf            # Main Nginx configuration
└── README.md
```

## Usage

Nginx is primarily used in production for:
- Reverse proxy to Django (Gunicorn)
- Serving Next.js static files
- SSL termination
- Load balancing

## Development

In development, Nginx is optional. Services are accessed directly:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

## Production

In production, Nginx routes all traffic:
- / → Next.js frontend
- /api → Django backend
- /static → Static files
- /media → User uploads
