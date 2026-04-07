#!/bin/bash
# ==================================================
# LankaCommerce Cloud - Development Stop Script
# ==================================================
# Purpose: Stop development environment
# Usage: ./docker/scripts/dev-stop.sh [options]
# Options:
#   --clean    Remove volumes (database data)
#   --prune    Remove all unused Docker resources
# ==================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Options
CLEAN=""
PRUNE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN="-v"
            shift
            ;;
        --prune)
            PRUNE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${YELLOW}=========================================="
echo "LankaCommerce Cloud - Stopping Development"
echo -e "==========================================${NC}"

cd "${PROJECT_ROOT}"

# Stop containers
echo -e "${YELLOW}Stopping Docker containers...${NC}"
docker compose down ${CLEAN}

if [ "${CLEAN}" = "-v" ]; then
    echo -e "${YELLOW}Volumes have been removed.${NC}"
fi

if [ "${PRUNE}" = true ]; then
    echo -e "${YELLOW}Pruning unused Docker resources...${NC}"
    docker system prune -f
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Development environment stopped."
echo -e "==========================================${NC}"
