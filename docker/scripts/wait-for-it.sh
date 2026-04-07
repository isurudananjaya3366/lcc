#!/bin/bash
# ==================================================
# LankaCommerce Cloud - Wait for Service Script
# ==================================================
# Purpose: Wait for a service to be available
# Usage: ./wait-for-it.sh host:port [-t timeout] [-- command]
# Example: ./wait-for-it.sh db:5432 -t 60 -- python manage.py migrate
# ==================================================

set -e

TIMEOUT=30
QUIET=0
HOST=""
PORT=""

usage() {
    echo "Usage: $0 host:port [-t timeout] [-q] [-- command args]"
    echo ""
    echo "Options:"
    echo "  -t TIMEOUT     Timeout in seconds (default: 30)"
    echo "  -q             Quiet mode, don't output status"
    echo "  -- COMMAND     Execute command after wait"
    exit 1
}

# Parse host:port
parse_hostport() {
    local hostport=$1
    HOST="${hostport%%:*}"
    PORT="${hostport##*:}"

    if [ -z "$HOST" ] || [ -z "$PORT" ]; then
        echo "Error: Invalid host:port format"
        usage
    fi
}

# Wait for TCP connection
wait_for_tcp() {
    local start_ts=$(date +%s)

    while :; do
        if nc -z "$HOST" "$PORT" > /dev/null 2>&1; then
            local end_ts=$(date +%s)
            [ "$QUIET" -eq 0 ] && echo "$HOST:$PORT is available after $((end_ts - start_ts)) seconds"
            return 0
        fi

        local current_ts=$(date +%s)
        if [ $((current_ts - start_ts)) -ge "$TIMEOUT" ]; then
            echo "Timeout: $HOST:$PORT not available after $TIMEOUT seconds"
            return 1
        fi

        sleep 1
    done
}

# Parse arguments
if [ $# -eq 0 ]; then
    usage
fi

parse_hostport "$1"
shift

while [ $# -gt 0 ]; do
    case "$1" in
        -t)
            TIMEOUT="$2"
            shift 2
            ;;
        -q)
            QUIET=1
            shift
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Wait for service
wait_for_tcp || exit 1

# Execute command if provided
if [ $# -gt 0 ]; then
    exec "$@"
fi
