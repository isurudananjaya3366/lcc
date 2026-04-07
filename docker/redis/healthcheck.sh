#!/bin/sh
# ==================================================
# LankaCommerce Cloud - Redis Health Check
# ==================================================
# Purpose: Check Redis server health
# Usage: Docker HEALTHCHECK instruction
# Exit: 0 = healthy, 1 = unhealthy
# ==================================================

# Check if Redis responds to PING
RESULT=$(redis-cli ping 2>/dev/null)

if [ "$RESULT" = "PONG" ]; then
    echo "Redis is healthy"
    exit 0
else
    echo "Redis is unhealthy: $RESULT"
    exit 1
fi
