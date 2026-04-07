#!/bin/bash
# ==================================================
# LankaCommerce Cloud - Branch Name Validation
# ==================================================
# Validates branch names follow naming conventions
# ==================================================

set -e

# Get current branch name
if [ -z "$1" ]; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
else
    BRANCH="$1"
fi

# Skip validation for main branches
if [[ "$BRANCH" == "main" || "$BRANCH" == "develop" ]]; then
    echo "✅ Branch '$BRANCH' is a main branch - OK"
    exit 0
fi

# Define valid patterns
FEATURE_PATTERN="^feature\/[A-Z]+-[0-9]+-[a-z0-9-]+$"
BUGFIX_PATTERN="^bugfix\/[A-Z]+-[0-9]+-[a-z0-9-]+$"
HOTFIX_PATTERN="^hotfix\/[0-9]+\.[0-9]+\.[0-9]+-[a-z0-9-]+$"
RELEASE_PATTERN="^release\/[0-9]+\.[0-9]+\.[0-9]+(-[a-z]+)?$"

# Check patterns
if [[ $BRANCH =~ $FEATURE_PATTERN ]]; then
    echo "✅ Branch '$BRANCH' follows feature naming convention - OK"
    exit 0
fi

if [[ $BRANCH =~ $BUGFIX_PATTERN ]]; then
    echo "✅ Branch '$BRANCH' follows bugfix naming convention - OK"
    exit 0
fi

if [[ $BRANCH =~ $HOTFIX_PATTERN ]]; then
    echo "✅ Branch '$BRANCH' follows hotfix naming convention - OK"
    exit 0
fi

if [[ $BRANCH =~ $RELEASE_PATTERN ]]; then
    echo "✅ Branch '$BRANCH' follows release naming convention - OK"
    exit 0
fi

# Invalid branch name
echo "❌ Invalid branch name: '$BRANCH'"
echo ""
echo "Valid patterns:"
echo "  feature/<TICKET>-<description>  (e.g., feature/LCC-123-user-auth)"
echo "  bugfix/<TICKET>-<description>   (e.g., bugfix/LCC-456-fix-login)"
echo "  hotfix/<version>-<description>  (e.g., hotfix/1.0.1-security-fix)"
echo "  release/<version>               (e.g., release/1.0.0)"
echo ""
exit 1
