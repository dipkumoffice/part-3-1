#!/bin/bash

set -e

ENV=$1
VERSION=$2

echo "🚀 Deploying Health Check Script"
echo "Environment: $ENV"
echo "Version: $VERSION"

# Simulate deployment (example: copy to deployment directory)
DEPLOY_DIR="/opt/healthcheck/$ENV"
mkdir -p "$DEPLOY_DIR"
cp scripts/health_check.py "$DEPLOY_DIR/"
echo "#!/bin/bash" > "$DEPLOY_DIR/run.sh"
echo "python3 health_check.py" >> "$DEPLOY_DIR/run.sh"
chmod +x "$DEPLOY_DIR/run.sh"

echo "✅ Deployed to $DEPLOY_DIR"
