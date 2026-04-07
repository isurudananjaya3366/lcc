#!/bin/bash
# ==================================================
# LankaCommerce Cloud - Development Start Script
# ==================================================
# Purpose: Start complete development environment
# Usage: ./docker/scripts/dev-start.sh [options]
# Options:
#   --build    Rebuild images before starting
#   --detach   Run in background (default)
#   --attach   Run in foreground
# ==================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Options
BUILD=""
MODE="-d"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD="--build"
            shift
            ;;
        --attach)
            MODE=""
            shift
            ;;
        --detach)
            MODE="-d"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${YELLOW}=========================================="
echo "LankaCommerce Cloud - Starting Development"
echo -e "==========================================${NC}"

# Change to project root
cd "${PROJECT_ROOT}"

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from .env.example${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}.env file created. Please review and update values.${NC}"
    else
        echo -e "${RED}Error: .env.example not found${NC}"
        exit 1
    fi
fi

# Start containers
echo -e "${YELLOW}Starting Docker containers...${NC}"
docker compose up ${BUILD} ${MODE}

if [ "${MODE}" = "-d" ]; then
    echo ""
    echo -e "${YELLOW}Waiting for services to be ready...${NC}"

    # Wait for database
    echo -n "Waiting for PostgreSQL... "
    timeout 60 bash -c 'until docker compose exec -T db pg_isready -U postgres > /dev/null 2>&1; do sleep 1; done' && \
        echo -e "${GREEN}Ready${NC}" || echo -e "${RED}Timeout${NC}"

    # Wait for Redis
    echo -n "Waiting for Redis... "
    timeout 30 bash -c 'until docker compose exec -T redis redis-cli ping > /dev/null 2>&1; do sleep 1; done' && \
        echo -e "${GREEN}Ready${NC}" || echo -e "${RED}Timeout${NC}"

    # Wait for backend
    echo -n "Waiting for Backend... "
    timeout 120 bash -c 'until curl -sf http://localhost:8000/health/ > /dev/null 2>&1; do sleep 2; done' && \
        echo -e "${GREEN}Ready${NC}" || echo -e "${YELLOW}May still be starting${NC}"

    # Wait for frontend
    echo -n "Waiting for Frontend... "
    timeout 120 bash -c 'until curl -sf http://localhost:3000 > /dev/null 2>&1; do sleep 2; done' && \
        echo -e "${GREEN}Ready${NC}" || echo -e "${YELLOW}May still be starting${NC}"

    echo ""
    echo -e "${GREEN}=========================================="
    echo "Development environment is ready!"
    echo "=========================================="
    echo ""
    echo "Services:"
    echo "  Backend API:  http://localhost:8000"
    echo "  Frontend:     http://localhost:3000"
    echo "  Flower:       http://localhost:5555"
    echo "  PostgreSQL:   localhost:5432"
    echo "  Redis:        localhost:6379"
    echo ""
    echo "Commands:"
    echo "  View logs:    docker compose logs -f"
    echo "  Stop:         ./docker/scripts/dev-stop.sh"
    echo -e "==========================================${NC}"
fi
